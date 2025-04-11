import { defineStore } from 'pinia'
import authService from '../services/authService'
import { ref, computed } from 'vue'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => user.value?.role === 'manager' || user.value?.role === 'admin')
  
  // 操作
  async function login(credentials) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.login(credentials)
      
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      
      // 存储令牌
      localStorage.setItem('token', token.value)
      localStorage.setItem('refreshToken', refreshToken.value)
      
      // 获取用户信息
      await fetchUserInfo()
      
      // 登录成功后重定向
      router.push({ name: 'Dashboard' })
      
      return true
    } catch (err) {
      console.error('Login error:', err)
      error.value = '用户名或密码错误'
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function fetchUserInfo() {
    try {
      if (!token.value) return
      
      loading.value = true
      const response = await authService.getCurrentUser()
      user.value = response.data
    } catch (err) {
      console.error('Error fetching user info:', err)
      // 如果令牌过期，尝试刷新令牌
      if (err.response && err.response.status === 401) {
        await refreshAccessToken()
      }
    } finally {
      loading.value = false
    }
  }
  
  async function refreshAccessToken() {
    try {
      if (!refreshToken.value) {
        // 没有刷新令牌，需要用户重新登录
        logout()
        return
      }
      
      const response = await authService.refreshToken(refreshToken.value)
      token.value = response.data.access
      localStorage.setItem('token', token.value)
      
      return true
    } catch (err) {
      console.error('Error refreshing token:', err)
      // 刷新令牌也过期，需要用户重新登录
      logout()
      return false
    }
  }
  
  async function logout() {
    // 清除所有状态和存储
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    
    // 重定向到登录页
    router.push({ name: 'Login' })
  }
  
  async function updateProfile(userData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.updateCurrentUser(userData)
      user.value = response.data
      
      return true
    } catch (err) {
      console.error('Error updating profile:', err)
      error.value = '更新个人信息失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 如果已经有令牌，尝试获取用户信息
  if (token.value) {
    fetchUserInfo()
  }
  
  return {
    // 状态
    token,
    refreshToken,
    user,
    loading,
    error,
    // 计算属性
    isAuthenticated,
    isAdmin,
    isManager,
    // 操作
    login,
    logout,
    fetchUserInfo,
    refreshAccessToken,
    updateProfile
  }
}) 