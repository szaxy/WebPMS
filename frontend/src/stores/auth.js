import { defineStore } from 'pinia'
import { ref } from 'vue'
// 后续会导入认证服务
// import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)
  
  // 获取状态
  const isAuthenticated = () => !!token.value
  
  // 操作
  const login = async (credentials) => {
    loading.value = true
    
    try {
      // 模拟登录
      // 实际项目中需要调用 API
      // const response = await authService.login(credentials)
      // token.value = response.data.access
      // localStorage.setItem('token', response.data.access)
      // localStorage.setItem('refreshToken', response.data.refresh)
      
      // 模拟设置token
      token.value = 'dummy-token'
      localStorage.setItem('token', 'dummy-token')
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: '用户名或密码错误' }
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }
  
  const fetchUserInfo = async () => {
    if (!isAuthenticated()) return
    
    loading.value = true
    
    try {
      // 实际项目中需要调用 API
      // const response = await authService.getProfile()
      // user.value = response.data
      
      // 模拟用户信息
      user.value = {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
        department: 'producer'
      }
      
      return { success: true }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return { success: false, error: '获取用户信息失败' }
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    token,
    user,
    loading,
    
    // 获取状态
    isAuthenticated,
    
    // 操作
    login,
    logout,
    fetchUserInfo
  }
}) 