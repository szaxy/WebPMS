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
      console.error('登录失败:', err)
      error.value = err.response?.data?.detail || '用户名或密码错误'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      await authService.register(userData)
      return { success: true }
    } catch (err) {
      console.error('注册失败:', err)
      error.value = '注册失败，请检查输入信息'
      
      // 提取API错误信息
      if (err.response?.data) {
        const errors = err.response.data
        error.value = Object.keys(errors)
          .map(key => `${key}: ${errors[key].join(', ')}`)
          .join('; ')
      }
      
      return { success: false, error: error.value }
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
      console.error('获取用户信息失败:', err)
      error.value = '获取用户信息失败'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const fetchUsers = async (params = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.getUsers(params)
      users.value = response.data
      return { success: true }
    } catch (err) {
      console.error('获取用户列表失败:', err)
      error.value = '获取用户列表失败'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const fetchPendingUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.getPendingUsers()
      pendingUsers.value = response.data
      return { success: true }
    } catch (err) {
      console.error('获取待审核用户失败:', err)
      error.value = '获取待审核用户失败'
      return { success: false, error: error.value }
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
      console.error('审核用户失败:', err)
      error.value = '审核用户失败'
      return { success: false, error: error.value }
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
    approveUser
  }
}) 