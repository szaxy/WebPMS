import axios from 'axios'

// 创建认证API客户端实例
const authClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
})

// API请求拦截器：添加认证令牌
authClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  // 用户登录
  login(credentials) {
    return authClient.post('/auth/login/', credentials)
  },
  
  // 用户注册
  register(userData) {
    return authClient.post('/auth/register/', userData)
  },
  
  // 刷新令牌
  refreshToken(refreshToken) {
    return authClient.post('/auth/refresh/', { refresh: refreshToken })
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return authClient.get('/users/me/')
  },
  
  // 更新当前用户信息
  updateCurrentUser(data) {
    return authClient.patch('/users/me/', data)
  },
  
  // 获取用户列表
  getUsers(params = {}) {
    return authClient.get('/users/', { params })
  },
  
  // 获取待审核用户
  getPendingUsers() {
    return authClient.get('/users/pending-approvals/')
  },
  
  // 审核用户
  approveUser(userId, data) {
    return authClient.post(`/users/${userId}/approve/`, data)
  },
  
  // 获取单个用户详情
  getUser(userId) {
    return authClient.get(`/users/${userId}/`)
  },
  
  // 更新用户
  updateUser(userId, data) {
    return authClient.patch(`/users/${userId}/`, data)
  },
  
  // 注销
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    
    // 可以添加额外的清理操作
    
    return Promise.resolve()
  }
} 