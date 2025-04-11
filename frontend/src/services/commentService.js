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
  // 获取评论列表
  getComments(params = {}) {
    return apiClient.get('/comments/comments/', { params })
  },
  
  // 获取单个评论详情
  getComment(id) {
    return apiClient.get(`/comments/comments/${id}/`)
  },
  
  // 创建新评论
  createComment(data) {
    return apiClient.post('/comments/comments/', data)
  },
  
  // 更新评论
  updateComment(id, data) {
    return apiClient.patch(`/comments/comments/${id}/`, data)
  },
  
  // 删除评论
  deleteComment(id) {
    return apiClient.delete(`/comments/comments/${id}/`)
  },
  
  // 标记评论为已解决/未解决
  resolveComment(id, isResolved = true) {
    return apiClient.patch(`/comments/comments/${id}/resolve/`, { is_resolved: isResolved })
  },
  
  // 获取评论的回复
  getCommentReplies(id) {
    return apiClient.get(`/comments/comments/${id}/replies/`)
  },
  
  // 上传附件
  uploadAttachment(formData) {
    return apiClient.post('/comments/attachments/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 删除附件
  deleteAttachment(id) {
    return apiClient.delete(`/comments/attachments/${id}/`)
  }
}