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

export default {
  // 获取项目列表
  getProjects(params = {}) {
    return apiClient.get('/projects/', { params })
  },
  
  // 获取单个项目详情
  getProject(id) {
    return apiClient.get(`/projects/${id}/`)
  },
  
  // 创建新项目
  createProject(data) {
    return apiClient.post('/projects/', data)
  },
  
  // 更新项目信息
  updateProject(id, data) {
    return apiClient.patch(`/projects/${id}/`, data)
  },
  
  // 删除项目
  deleteProject(id) {
    return apiClient.delete(`/projects/${id}/`)
  },
  
  // 获取项目下的镜头
  getProjectShots(id) {
    return apiClient.get(`/projects/${id}/shots/`)
  },
  
  // 更新项目状态
  updateProjectStatus(id, status) {
    return apiClient.patch(`/projects/${id}/update_status/`, { status })
  },
  
  // 获取项目统计数据
  getProjectStats(id) {
    return apiClient.get(`/projects/${id}/stats/`)
  }
} 