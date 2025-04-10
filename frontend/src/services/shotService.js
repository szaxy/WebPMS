import axios from 'axios'

// 创建API客户端实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
})

// 请求拦截器 - 添加认证令牌
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理常见错误
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 401未授权，触发登出
    if (error.response && error.response.status === 401) {
      // 这里可以调用store的登出方法
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // 获取镜头列表
  getShots(params = {}) {
    return apiClient.get('/shots/', { params })
  },
  
  // 获取单个镜头详情
  getShot(id) {
    return apiClient.get(`/shots/${id}/`)
  },
  
  // 创建新镜头
  createShot(data) {
    return apiClient.post('/shots/', data)
  },
  
  // 更新镜头信息
  updateShot(id, data) {
    return apiClient.patch(`/shots/${id}/`, data)
  },
  
  // 删除镜头
  deleteShot(id) {
    return apiClient.delete(`/shots/${id}/`)
  },
  
  // 获取镜头历史记录
  getShotHistory(id) {
    return apiClient.get(`/shots/${id}/history/`)
  },
  
  // 获取镜头反馈列表
  getShotComments(id) {
    return apiClient.get(`/shots/${id}/comments/`)
  },
  
  // 添加镜头反馈
  addShotComment(id, data) {
    return apiClient.post(`/shots/${id}/comments/`, data)
  }
} 