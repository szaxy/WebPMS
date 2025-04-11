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
    console.log('项目API调用，参数:', params)
    return apiClient.get('/projects/', { params })
      .then(response => {
        console.log('项目API响应状态:', response.status)
        console.log('项目API响应数据类型:', typeof response.data, Array.isArray(response.data) ? '是数组' : '不是数组')
        if (Array.isArray(response.data)) {
          console.log('项目数据长度:', response.data.length)
        } else if (response.data && response.data.results) {
          console.log('项目分页数据 - 总数:', response.data.count, '当前页数量:', response.data.results.length)
        }
        return response
      })
      .catch(error => {
        console.error('获取项目API错误:', error.message)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
        }
        throw error
      })
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