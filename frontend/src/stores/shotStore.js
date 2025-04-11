import { defineStore } from 'pinia'
import shotService from '../services/shotService'
import { ref, computed } from 'vue'
import { useUserStore } from './userStore'

export const useShotStore = defineStore('shot', () => {
  // 状态
  const shots = ref([])
  const selectedShot = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const totalShots = ref(0)
  const pagination = ref({
    page: 1,
    limit: 50,
  })
  const filters = ref({
    project: null,
    status: null,
    prom_stage: null,
    artist: null,
    department: null,
    search: '',
  })
  const selectedShotIds = ref([])
  const shotNotes = ref([])
  const visibleColumns = ref([
    'shot_code',
    'prom_stage', 
    'status', 
    'artist_name',
    'duration_frame',
    'deadline',
    'last_submit_date'
  ])

  // 计算属性
  const userStore = useUserStore()
  
  const canFilterByDepartment = computed(() => {
    return userStore.isAdmin || userStore.currentUser?.department === 'producer'
  })
  
  const shotsByStatus = computed(() => {
    const grouped = {
      'in_progress': [],
      'review': [],
      'approved': [],
      'need_revision': [],
    }
    
    shots.value.forEach(shot => {
      if (grouped[shot.status]) {
        grouped[shot.status].push(shot)
      }
    })
    
    return grouped
  })
  
  const getStatusText = (status) => {
    const statusMap = {
      'in_progress': '制作中',
      'review': '审核中',
      'approved': '已通过',
      'need_revision': '需修改',
    }
    return statusMap[status] || status
  }
  
  // 动作
  const fetchShots = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      // 使用传入的参数，如果没有传入则使用store中的filters和pagination
      const queryParams = {
        page: params.page || pagination.value.page,
        limit: params.limit || pagination.value.limit,
      }
      
      // 添加筛选条件，优先使用传入的参数，否则使用store中的
      if (params.project || filters.value.project) queryParams.project = params.project || filters.value.project;
      if (params.status || filters.value.status) queryParams.status = params.status || filters.value.status;
      if (params.prom_stage || filters.value.prom_stage) queryParams.prom_stage = params.prom_stage || filters.value.prom_stage;
      if (params.artist || filters.value.artist) queryParams.artist = params.artist || filters.value.artist;
      if ((params.department || filters.value.department) && canFilterByDepartment.value) {
        queryParams.department = params.department || filters.value.department;
      }
      if (params.search || filters.value.search) queryParams.search = params.search || filters.value.search;
      
      const response = await shotService.getShots(queryParams)
      
      // 检查响应格式
      if (response.data && Array.isArray(response.data.results)) {
        // 标准分页响应
        shots.value = response.data.results
        if (response.data.count !== undefined) {
          totalShots.value = response.data.count
        }
      } else if (response.data && Array.isArray(response.data)) {
        // 直接返回数组
        shots.value = response.data
        totalShots.value = response.data.length
      } else if (response.data && response.data.shots) {
        // API根路径返回了资源URL，需要再次请求shots
        console.log('API返回了资源URL，正在获取shots资源')
        try {
          const shotsResponse = await shotService.getShotsFromURL(response.data.shots)
          if (shotsResponse.data && Array.isArray(shotsResponse.data.results)) {
            shots.value = shotsResponse.data.results
            totalShots.value = shotsResponse.data.count || shotsResponse.data.results.length
          } else if (shotsResponse.data && Array.isArray(shotsResponse.data)) {
            shots.value = shotsResponse.data
            totalShots.value = shotsResponse.data.length
          } else {
            console.error('二次请求获取shots资源失败:', shotsResponse.data)
            shots.value = []
            totalShots.value = 0
          }
        } catch (nestedErr) {
          console.error('获取shots资源URL失败:', nestedErr)
          shots.value = []
          totalShots.value = 0
        }
      } else if (response.data) {
        // 非预期格式但有数据，记录错误并设置为空数组
        console.error('Unexpected API response format:', response.data)
        shots.value = []
        totalShots.value = 0
      } else {
        // 没有数据
        shots.value = []
        totalShots.value = 0
      }
    } catch (err) {
      console.error('Error fetching shots:', err)
      error.value = '获取镜头列表失败'
      shots.value = [] // 确保出错时也设置为空数组
      totalShots.value = 0
    } finally {
      loading.value = false
    }
  }
  
  const fetchShotById = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.getShotById(id)
      selectedShot.value = response.data
    } catch (err) {
      console.error('Error fetching shot details:', err)
      error.value = '获取镜头详情失败'
    } finally {
      loading.value = false
    }
  }
  
  const fetchShotNotes = async (shotId) => {
    loading.value = true
    
    try {
      const response = await shotService.getShotNotes({ shot: shotId })
      shotNotes.value = response.data.results || response.data
    } catch (err) {
      console.error('Error fetching shot notes:', err)
    } finally {
      loading.value = false
    }
  }
  
  const updateShot = async (id, data) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.updateShot(id, data)
      
      // 更新本地数据
      if (selectedShot.value && selectedShot.value.id === id) {
        selectedShot.value = { ...selectedShot.value, ...response.data }
      }
      
      // 更新列表中的镜头
      const index = shots.value.findIndex(shot => shot.id === id)
      if (index !== -1) {
        shots.value[index] = { ...shots.value[index], ...response.data }
      }
      
      return response.data
    } catch (err) {
      console.error('Error updating shot:', err)
      error.value = '更新镜头失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const bulkUpdateShots = async (updateData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.bulkUpdateShots({
        shot_ids: selectedShotIds.value,
        ...updateData
      })
      
      // 刷新镜头列表
      await fetchShots()
      
      return response.data
    } catch (err) {
      console.error('Error bulk updating shots:', err)
      error.value = '批量更新镜头失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const bulkRenameShots = async (renameData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.bulkRenameShots({
        shot_ids: selectedShotIds.value,
        ...renameData
      })
      
      // 刷新镜头列表
      await fetchShots()
      
      return response.data
    } catch (err) {
      console.error('Error bulk renaming shots:', err)
      error.value = '批量重命名镜头失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const addShot = async (shotData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.createShot(shotData)
      
      // 刷新镜头列表
      await fetchShots()
      
      return response.data
    } catch (err) {
      console.error('Error adding shot:', err)
      error.value = '添加镜头失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createShotNote = async (noteData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.createShotNote(noteData)
      
      // 如果是当前选中镜头的备注，添加到列表
      if (selectedShot.value && selectedShot.value.id === noteData.shot) {
        shotNotes.value = [response.data, ...shotNotes.value]
      }
      
      return response.data
    } catch (err) {
      console.error('Error creating shot note:', err)
      error.value = '添加镜头备注失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const submitShot = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await shotService.submitShot(id)
      
      // 检查是否有重要备注需要确认
      if (response.data.important_notes) {
        return response.data // 返回重要备注信息，由组件处理确认流程
      }
      
      // 如果成功提交，更新本地数据
      if (selectedShot.value && selectedShot.value.id === id) {
        selectedShot.value.status = 'review'
        selectedShot.value.last_submit_date = new Date().toISOString().split('T')[0]
      }
      
      // 更新列表中的镜头
      const index = shots.value.findIndex(shot => shot.id === id)
      if (index !== -1) {
        shots.value[index].status = 'review'
        shots.value[index].last_submit_date = new Date().toISOString().split('T')[0]
      }
      
      return response.data
    } catch (err) {
      console.error('Error submitting shot:', err)
      error.value = '提交镜头失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 重置选择
  const resetSelection = () => {
    selectedShotIds.value = []
  }
  
  // 切换可见列
  const toggleColumnVisibility = (columnName) => {
    const index = visibleColumns.value.indexOf(columnName)
    if (index !== -1) {
      visibleColumns.value.splice(index, 1)
    } else {
      visibleColumns.value.push(columnName)
    }
  }
  
  return {
    // 状态
    shots,
    selectedShot,
    loading,
    error,
    totalShots,
    pagination,
    filters,
    selectedShotIds,
    shotNotes,
    visibleColumns,
    
    // 计算属性
    canFilterByDepartment,
    shotsByStatus,
    getStatusText,
    
    // 动作
    fetchShots,
    fetchShotById,
    fetchShotNotes,
    updateShot,
    bulkUpdateShots,
    bulkRenameShots,
    addShot,
    createShotNote,
    submitShot,
    resetSelection,
    toggleColumnVisibility
  }
}) 