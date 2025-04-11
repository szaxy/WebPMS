import { defineStore } from 'pinia'
import shotService from '../services/shotService'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useShotStore = defineStore('shot', () => {
  // 状态
  const shots = ref([])
  const currentShot = ref(null)
  const shotNotes = ref([])
  const loading = ref(false)
  const error = ref(null)
  const selectedShotIds = ref([])
  
  // 计算属性
  const shotsByStatus = computed(() => {
    // 使用规范中定义的状态
    const grouped = {
      'waiting': [],
      'in_progress': [],
      'submit_review': [],
      'revising': [],
      'internal_approved': [],
      'client_review': [],
      'client_rejected': [],
      'client_approved': [],
      'client_revision': [],
      'deleted_merged': [],
      'suspended': [],
      'completed': []
    }
    
    shots.value.forEach(shot => {
      if (grouped[shot.status]) {
        grouped[shot.status].push(shot)
      } else {
        grouped['waiting'].push(shot)
      }
    })
    
    return grouped
  })
  
  const selectedShots = computed(() => {
    return shots.value.filter(shot => selectedShotIds.value.includes(shot.id))
  })
  
  const hasSelectedShots = computed(() => {
    return selectedShotIds.value.length > 0
  })
  
  const shotsCount = computed(() => shots.value.length)
  
  // 操作
  async function fetchShots(params = {}) {
    try {
      loading.value = true
      error.value = null
      
      console.log('fetchShots开始请求，参数:', params)
      const response = await shotService.getShots(params)
      console.log('镜头API响应数据类型:', typeof response.data)
      
      // 详细检查响应结构，支持多种格式
      if (response.data) {
        // 检查DRF分页格式
        if (response.data.results && Array.isArray(response.data.results)) {
          // 标准DRF分页格式
          shots.value = response.data.results
          console.log('成功获取镜头数据(分页):', shots.value.length, '条记录')
          return response.data
        } 
        // 检查数组格式
        else if (Array.isArray(response.data)) {
          // 直接数组格式
          shots.value = response.data
          console.log('成功获取镜头数据(非分页):', shots.value.length, '条记录')
          return {
            count: response.data.length,
            results: response.data
          }
        }
        // 检查是否为路由器根响应(对象且包含shots属性)
        else if (typeof response.data === 'object' && response.data.shots) {
          // 这是DRF路由器根响应，需要再发一个请求获取真正的数据
          console.log('收到API根目录信息，尝试获取真正的镜头数据:', response.data.shots)
          
          try {
            // 进行第二次请求，使用apiClient而非axios，确保带上token
            const shotResponse = await shotService.getShotsFromUrl(response.data.shots)
            if (shotResponse.data.results && Array.isArray(shotResponse.data.results)) {
              shots.value = shotResponse.data.results
              console.log('第二次请求成功获取镜头数据(分页):', shots.value.length, '条记录')
              return shotResponse.data
            } else if (Array.isArray(shotResponse.data)) {
              shots.value = shotResponse.data
              console.log('第二次请求成功获取镜头数据(非分页):', shots.value.length, '条记录')
              return {
                count: shotResponse.data.length,
                results: shotResponse.data
              }
            }
          } catch (secondError) {
            console.error('第二次请求失败:', secondError)
            error.value = '获取镜头列表失败，请联系管理员'
            shots.value = []
          }
        }
        else {
          // 其他未知格式
          console.error('API返回数据格式不正确:', response.data)
          console.error('数据类型:', typeof response.data)
          console.error('属性:', Object.keys(response.data))
          error.value = '服务器返回数据格式不正确'
          shots.value = []
        }
      } else {
        console.error('API未返回任何数据')
        error.value = 'API未返回任何数据'
        shots.value = []
      }
      
      return {
        count: 0,
        results: []
      }
    } catch (err) {
      console.error('获取镜头列表失败:', err)
      if (err.response) {
        console.error('HTTP状态码:', err.response.status)
        console.error('错误响应数据:', err.response.data)
        
        if (err.response.status === 403) {
          error.value = '您没有权限查看此项目的镜头'
        } else if (err.response.status === 404) {
          error.value = '没有找到镜头数据，请确认项目是否存在'
        } else {
          error.value = `获取镜头列表失败: ${err.response.status}`
        }
      } else if (err.request) {
        console.error('请求未收到响应:', err.request)
        error.value = '服务器未响应，请检查网络连接'
      } else {
        error.value = `获取镜头列表失败: ${err.message}`
      }
      
      shots.value = []
      return {
        count: 0,
        results: []
      }
    } finally {
      loading.value = false
    }
  }
  
  async function fetchShot(id) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.getShot(id)
      currentShot.value = response.data
      
      return currentShot.value
    } catch (err) {
      console.error(`Error fetching shot ${id}:`, err)
      error.value = '获取镜头详情失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function createShot(shotData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.createShot(shotData)
      const newShot = response.data
      
      // 更新本地状态
      shots.value.push(newShot)
      
      return newShot
    } catch (err) {
      console.error('Error creating shot:', err)
      error.value = '创建镜头失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function updateShot(id, shotData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.updateShot(id, shotData)
      const updatedShot = response.data
      
      // 更新本地状态
      const index = shots.value.findIndex(s => s.id === id)
      if (index !== -1) {
        shots.value[index] = updatedShot
      }
      
      if (currentShot.value && currentShot.value.id === id) {
        currentShot.value = updatedShot
      }
      
      return updatedShot
    } catch (err) {
      console.error(`Error updating shot ${id}:`, err)
      error.value = '更新镜头失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function updateShotStatus(id, newStatus) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.updateShotStatus(id, newStatus)
      const updatedShot = response.data
      
      // 更新本地状态
      const index = shots.value.findIndex(s => s.id === id)
      if (index !== -1) {
        shots.value[index] = updatedShot
      }
      
      if (currentShot.value && currentShot.value.id === id) {
        currentShot.value = updatedShot
      }
      
      // 检查是否返回了重要备注提示
      const importantNotes = updatedShot.important_notes
      
      return { 
        shot: updatedShot,
        importantNotes: importantNotes || []
      }
    } catch (err) {
      console.error(`Error updating shot status ${id}:`, err)
      error.value = '更新镜头状态失败'
      return { shot: null, importantNotes: [] }
    } finally {
      loading.value = false
    }
  }
  
  async function deleteShot(id) {
    try {
      loading.value = true
      error.value = null
      
      await shotService.deleteShot(id)
      
      // 更新本地状态
      const index = shots.value.findIndex(s => s.id === id)
      if (index !== -1) {
        shots.value.splice(index, 1)
      }
      
      // 清除已选择的镜头
      selectedShotIds.value = selectedShotIds.value.filter(shotId => shotId !== id)
      
      // 清除当前镜头
      if (currentShot.value && currentShot.value.id === id) {
        currentShot.value = null
      }
      
      return true
    } catch (err) {
      console.error(`Error deleting shot ${id}:`, err)
      error.value = '删除镜头失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function batchUpdateShots(ids, fields) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.batchUpdateShots(ids, fields)
      
      // 重新获取镜头列表以确保状态同步
      await fetchShots()
      
      return response.data
    } catch (err) {
      console.error('Error batch updating shots:', err)
      error.value = '批量更新镜头失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function batchRenameShots(ids, options) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.batchRenameShots(ids, options)
      
      // 重新获取镜头列表以确保状态同步
      await fetchShots()
      
      return response.data
    } catch (err) {
      console.error('Error batch renaming shots:', err)
      error.value = '批量重命名镜头失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function fetchShotNotes(shotId) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.getShotNotes(shotId)
      shotNotes.value = response.data
      
      return shotNotes.value
    } catch (err) {
      console.error(`Error fetching shot notes for shot ${shotId}:`, err)
      error.value = '获取镜头备注失败'
      return []
    } finally {
      loading.value = false
    }
  }
  
  async function addShotNote(shotId, noteData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.addShotNote(shotId, noteData)
      const newNote = response.data
      
      // 更新本地状态
      shotNotes.value.unshift(newNote) // 添加到开头
      
      return newNote
    } catch (err) {
      console.error(`Error adding note to shot ${shotId}:`, err)
      error.value = '添加镜头备注失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function updateShotNote(noteId, noteData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.updateShotNote(noteId, noteData)
      const updatedNote = response.data
      
      // 更新本地状态
      const index = shotNotes.value.findIndex(n => n.id === noteId)
      if (index !== -1) {
        shotNotes.value[index] = updatedNote
      }
      
      return updatedNote
    } catch (err) {
      console.error(`Error updating note ${noteId}:`, err)
      error.value = '更新镜头备注失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function deleteShotNote(noteId) {
    try {
      loading.value = true
      error.value = null
      
      await shotService.deleteShotNote(noteId)
      
      // 更新本地状态
      const index = shotNotes.value.findIndex(n => n.id === noteId)
      if (index !== -1) {
        shotNotes.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      console.error(`Error deleting note ${noteId}:`, err)
      error.value = '删除镜头备注失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 选择镜头
  function selectShot(id) {
    if (!selectedShotIds.value.includes(id)) {
      selectedShotIds.value.push(id)
    }
  }
  
  // 取消选择镜头
  function deselectShot(id) {
    selectedShotIds.value = selectedShotIds.value.filter(shotId => shotId !== id)
  }
  
  // 切换选择镜头
  function toggleShotSelection(id) {
    if (selectedShotIds.value.includes(id)) {
      deselectShot(id)
    } else {
      selectShot(id)
    }
  }
  
  // 全选/全不选
  function selectAllShots(select = true) {
    if (select) {
      selectedShotIds.value = shots.value.map(shot => shot.id)
    } else {
      selectedShotIds.value = []
    }
  }
  
  return {
    // 状态
    shots,
    currentShot,
    shotNotes,
    loading,
    error,
    selectedShotIds,
    
    // 计算属性
    shotsByStatus,
    selectedShots,
    hasSelectedShots,
    shotsCount,
    
    // 操作
    fetchShots,
    fetchShot,
    createShot,
    updateShot,
    updateShotStatus,
    deleteShot,
    batchUpdateShots,
    batchRenameShots,
    fetchShotNotes,
    addShotNote,
    updateShotNote,
    deleteShotNote,
    
    // 选择操作
    selectShot,
    deselectShot,
    toggleShotSelection,
    selectAllShots
  }
}) 