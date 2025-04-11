import { defineStore } from 'pinia'
import shotService from '../services/shotService'
import { ref, computed } from 'vue'

export const useShotStore = defineStore('shot', () => {
  // 状态
  const shots = ref([])
  const currentShot = ref(null)
  const shotComments = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const shotsByStatus = computed(() => {
    const grouped = {
      'in_progress': [],
      'review': [],
      'approved': [],
      'need_revision': []
    }
    
    shots.value.forEach(shot => {
      if (grouped[shot.status]) {
        grouped[shot.status].push(shot)
      } else {
        grouped['in_progress'].push(shot)
      }
    })
    
    return grouped
  })
  
  const inProgressShots = computed(() => 
    shots.value.filter(s => s.status === 'in_progress')
  )
  
  const reviewShots = computed(() => 
    shots.value.filter(s => s.status === 'review')
  )
  
  const approvedShots = computed(() => 
    shots.value.filter(s => s.status === 'approved')
  )
  
  const needRevisionShots = computed(() => 
    shots.value.filter(s => s.status === 'need_revision')
  )
  
  const shotsCount = computed(() => shots.value.length)
  
  // 操作
  async function fetchShots(params = {}) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.getShots(params)
      shots.value = response.data
      
      return shots.value
    } catch (err) {
      console.error('Error fetching shots:', err)
      error.value = '获取镜头列表失败'
      return []
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
  
  async function updateShotStatus(id, status) {
    try {
      const response = await shotService.updateShot(id, { status })
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
      console.error(`Error updating shot status ${id}:`, err)
      throw err
    }
  }
  
  async function fetchShotComments(shotId) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.getShotComments(shotId)
      shotComments.value = response.data
      
      return shotComments.value
    } catch (err) {
      console.error(`Error fetching comments for shot ${shotId}:`, err)
      error.value = '获取镜头反馈失败'
      return []
    } finally {
      loading.value = false
    }
  }
  
  async function addShotComment(shotId, commentData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await shotService.addShotComment(shotId, commentData)
      const newComment = response.data
      
      // 更新本地状态
      shotComments.value.push(newComment)
      
      return newComment
    } catch (err) {
      console.error(`Error adding comment to shot ${shotId}:`, err)
      error.value = '添加反馈失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    shots,
    currentShot,
    shotComments,
    loading,
    error,
    // 计算属性
    shotsByStatus,
    inProgressShots,
    reviewShots,
    approvedShots,
    needRevisionShots,
    shotsCount,
    // 操作
    fetchShots,
    fetchShot,
    createShot,
    updateShot,
    updateShotStatus,
    fetchShotComments,
    addShotComment
  }
}) 