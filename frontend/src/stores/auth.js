import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const users = ref([])
  const pendingUsers = ref([])
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isSupervisor = computed(() => user.value?.role === 'supervisor' || isAdmin.value)
  const isLeader = computed(() => user.value?.role === 'leader' || isSupervisor.value)
  
  // 错误处理函数
  const handleError = (err, defaultMessage) => {
    console.error(defaultMessage, err)
    
    // 处理API错误
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else if (err.response?.data) {
      // 如果是表单错误（对象形式）
      if (typeof err.response.data === 'object' && !Array.isArray(err.response.data)) {
        error.value = Object.keys(err.response.data)
          .map(key => `${key}: ${err.response.data[key]}`)
          .join('; ')
      } else {
        error.value = err.response.data
      }
    } else {
      error.value = defaultMessage
    }
    
    return { success: false, error: error.value }
  }
  
  // 清除错误信息
  const clearError = () => {
    error.value = null
  }
  
  // 操作
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.login(credentials)
      token.value = response.data.access
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)
      
      // 登录后立即获取用户信息
      await fetchUserInfo()
      
      return { success: true }
    } catch (err) {
      return handleError(err, '用户名或密码错误')
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      // 转换设备代号为大写
      if (userData.device_code) {
        userData.device_code = userData.device_code.toUpperCase()
      }
      
      await authService.register(userData)
      return { success: true }
    } catch (err) {
      return handleError(err, '注册失败，请检查输入信息')
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    authService.logout()
  }
  
  const fetchUserInfo = async () => {
    if (!isAuthenticated.value) return { success: false }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.getCurrentUser()
      user.value = response.data
      return { success: true }
    } catch (err) {
      return handleError(err, '获取用户信息失败')
    } finally {
      loading.value = false
    }
  }
  
  const fetchUsers = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.getUsers(params)
      // 确保users.value是数组
      users.value = Array.isArray(response.data) ? response.data : []
      console.log('获取到用户列表:', users.value.length, '条记录')
      return { success: true }
    } catch (err) {
      console.error('获取用户列表失败:', err)
      error.value = err.response?.data?.message || err.message || '获取用户列表失败'
      return { 
        success: false, 
        error: error.value
      }
    } finally {
      loading.value = false
    }
  }
  
  const fetchPendingUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('调用获取待审核用户API')
      const response = await authService.getPendingUsers()
      console.log('获取到待审核用户数据:', response.data.length)
      pendingUsers.value = response.data
      return { success: true }
    } catch (err) {
      return handleError(err, '获取待审核用户失败')
    } finally {
      loading.value = false
    }
  }
  
  const approveUser = async (userId, data) => {
    loading.value = true
    error.value = null
    
    try {
      await authService.approveUser(userId, data)
      await fetchPendingUsers() // 刷新待审核用户列表
      return { success: true }
    } catch (err) {
      return handleError(err, '审核用户失败')
    } finally {
      loading.value = false
    }
  }
  
  const updateUser = async (userId, userData) => {
    loading.value = true
    error.value = null
    
    try {
      await authService.updateUser(userId, userData)
      return { success: true }
    } catch (err) {
      return handleError(err, '更新用户信息失败')
    } finally {
      loading.value = false
    }
  }
  
  const deleteUser = async (userId) => {
    loading.value = true
    error.value = null
    
    try {
      await authService.deleteUser(userId)
      return { success: true }
    } catch (err) {
      return handleError(err, '删除用户失败')
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    token,
    user,
    users,
    pendingUsers,
    loading,
    error,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    isSupervisor,
    isLeader,
    
    // 操作
    login,
    register,
    logout,
    fetchUserInfo,
    fetchUsers,
    fetchPendingUsers,
    approveUser,
    updateUser,
    deleteUser,
    clearError
  }
}) 