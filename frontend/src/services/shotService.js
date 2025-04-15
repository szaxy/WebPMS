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
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // 获取镜头列表
  getShots(params = {}) {
    console.log('获取镜头列表，参数:', params)
    
    // 参数处理，确保分页参数名称正确
    const apiParams = { ...params }
    
    // 确保分页参数正确传递
    if (apiParams.page_size) {
      // 有些后端API使用limit/offset而不是page/page_size
      // 根据你的API格式选择正确的参数名称
      
      // 如果后端使用limit/offset格式，则转换page/page_size
      // apiParams.limit = apiParams.page_size
      // apiParams.offset = (apiParams.page - 1) * apiParams.page_size
      // delete apiParams.page_size
      // delete apiParams.page
      
      // 或者保持page_size/page格式
      // 确保数值类型正确
      apiParams.page_size = parseInt(apiParams.page_size, 10)
      if (apiParams.page) {
        apiParams.page = parseInt(apiParams.page, 10)
      }
    }
    
    console.log('转换后的API参数:', apiParams)
    
    // 直接使用标准shots端点获取列表
    return apiClient.get('/shots/', { params: apiParams })
      .then(response => {
        console.log('镜头列表响应状态:', response.status)
        console.log('镜头列表数据类型:', typeof response.data, Array.isArray(response.data) ? '是数组' : '不是数组')
        if (typeof response.data === 'object' && !Array.isArray(response.data)) {
          console.log('响应对象属性:', Object.keys(response.data))
          if (response.data.results) {
            console.log('获取到分页结果，共', response.data.results.length, '条，总数:', response.data.count)
            console.log('分页信息: 页码', apiParams.page || 1, '每页', apiParams.page_size || '默认')
          }
        }
        return response
      })
      .catch(error => {
        console.error('获取镜头列表失败:', error.message)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
          console.error('错误头信息:', error.response.headers)
        } else if (error.request) {
          console.error('请求未收到响应')
        }
        throw error
      })
  },
  
  // 从完整URL获取镜头列表
  getShotsFromUrl(url, params = {}) {
    console.log('从URL获取镜头列表:', url)
    console.log('携带参数:', params)
    
    // 提取相对路径
    const relativeUrl = url.replace(/^https?:\/\/[^\/]+\/api/, '');
    console.log('转换为相对路径:', relativeUrl)
    
    return apiClient.get(relativeUrl, { params })
      .then(response => {
        console.log('URL请求响应状态:', response.status)
        console.log('URL请求数据类型:', typeof response.data, Array.isArray(response.data) ? '是数组' : '不是数组')
        return response
      })
      .catch(error => {
        console.error('从URL获取镜头列表失败:', error.message)
        throw error
      })
  },
  
  // 获取单个镜头详情
  getShot(id) {
    return apiClient.get(`/shots/${id}/`)
  },
  
  // 创建新镜头
  createShot(data) {
    // 确保请求数据符合API规范
    const shotData = {
      project: data.project,
      shot_code: data.shot_code,
      duration_frame: data.duration_frame || 24,
      framepersecond: data.framepersecond || 24,
      prom_stage: data.prom_stage || 'LAY',
      status: data.status || 'waiting',
      description: data.description || ''
    }
    
    // 处理日期字段 - 增强日期值处理逻辑
    if (data.deadline) {
      // 处理Date对象
      if (data.deadline instanceof Date && !isNaN(data.deadline.getTime())) {
        // 有效的Date对象，转换为YYYY-MM-DD格式
        shotData.deadline = data.deadline.toISOString().split('T')[0]
      } 
      // 处理字符串
      else if (typeof data.deadline === 'string') {
        const trimmed = data.deadline.trim()
        if (trimmed && /^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
          shotData.deadline = trimmed
        }
      }
      // 其他情况不发送日期字段
    }
    
    if (data.last_submit_date) {
      // 处理Date对象
      if (data.last_submit_date instanceof Date && !isNaN(data.last_submit_date.getTime())) {
        // 有效的Date对象，转换为YYYY-MM-DD格式
        shotData.last_submit_date = data.last_submit_date.toISOString().split('T')[0]
      } 
      // 处理字符串
      else if (typeof data.last_submit_date === 'string') {
        const trimmed = data.last_submit_date.trim()
        if (trimmed && /^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
          shotData.last_submit_date = trimmed
        }
      }
      // 其他情况不发送日期字段
    }
    
    // 如果提供了制作者ID，添加到请求数据
    if (data.artist) {
      shotData.artist = data.artist
    }
    
    console.log('准备创建镜头，请求数据:', shotData)
    // 使用标准REST端点，不需要create/
    return apiClient.post('/shots/', shotData)
      .then(response => {
        console.log('创建镜头API响应:', response.status)
        return response
      })
      .catch(error => {
        console.error('创建镜头API错误:', error)
        throw error
      })
  },
  
  // 更新镜头信息
  updateShot(id, data) {
    return apiClient.patch(`/shots/${id}/`, data)
  },
  
  // 更新镜头状态
  updateShotStatus(id, status) {
    return apiClient.patch(`/shots/${id}/update_status/`, { status })
  },
  
  // 删除镜头
  deleteShot(id) {
    console.log(`尝试删除镜头，ID: ${id}`)
    return apiClient.delete(`/shots/${id}/`)
      .then(response => {
        console.log(`删除成功响应:`, response)
        return response
      })
      .catch(error => {
        console.error(`删除失败，ID: ${id}, 错误:`, error)
        if (error.response) {
          console.error('状态码:', error.response.status)
          console.error('响应数据:', error.response.data)
        }
        throw error
      })
  },
  
  // 批量更新镜头
  batchUpdateShots(ids, fields) {
    return apiClient.post('/shots/batch-update/', { ids, fields })
  },
  
  // 批量重命名镜头
  batchRenameShots(ids, options) {
    return apiClient.post('/shots/batch-rename/', { 
      ids,
      prefix: options.prefix || '',
      suffix: options.suffix || '',
      start_num: options.startNum || 10,
      step: options.step || 10,
      digit_count: options.digitCount || 4
    })
  },
  
  // 获取镜头备注列表
  getShotNotes(shotId) {
    // 使用shot-notes端点并以查询参数传递shot_id
    console.log(`正在获取镜头 ${shotId} 的备注`)
    return apiClient.get(`/shot-notes/`, { params: { shot: shotId } })
      .then(response => {
        console.log(`成功获取镜头 ${shotId} 的备注:`, response.data)
        return response
      })
      .catch(error => {
        console.error(`获取镜头 ${shotId} 备注失败:`, error)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
        }
        throw error
      })
  },
  
  // 添加镜头备注
  addShotNote(shotId, data) {
    // 创建备注数据，确保添加shot字段
    const noteData = { ...data, shot: shotId }
    
    // 注释掉或删除以下逻辑，保留attachment_data字段，即使它是空数组
    /*
    // 只在有附件时添加attachment_data字段
    if (data.attachment_data && data.attachment_data.length > 0) {
      // 保留原有的attachment_data
    } else {
      // 如果没有附件数据，确保不发送空数组
      delete noteData.attachment_data
    }
    */
    
    console.log(`正在添加镜头 ${shotId} 的备注:`, noteData)
    
    // 修改API路径，使用 with_attachment 端点
    return apiClient.post(`/shot-notes/with_attachment/`, noteData)
      .then(response => {
        console.log(`成功添加镜头 ${shotId} 的备注:`, response.data)
        return response
      })
      .catch(error => {
        console.error(`添加镜头 ${shotId} 的备注失败:`, error)
        if (error.response) {
          console.error('错误状态:', error.response.status)
          console.error('错误数据:', error.response.data)
        }
        throw error
      })
  },
  
  // 更新镜头备注
  updateShotNote(noteId, data) {
    const noteData = {}
    if (data.content !== undefined) noteData.content = data.content
    if (data.is_important !== undefined) noteData.is_important = data.is_important
    
    return apiClient.patch(`/shot-notes/${noteId}/`, noteData)
  },
  
  // 删除镜头备注
  deleteShotNote(noteId) {
    return apiClient.delete(`/shot-notes/${noteId}/`)
  },
  
  // 获取镜头历史记录
  getShotHistory(id) {
    return apiClient.get(`/shots/${id}/history/`)
  },
  
  // 获取镜头反馈列表
  getShotComments(id) {
    return apiClient.get(`/comments/comments/`, { params: { shot: id } })
  },
  
  // 添加镜头反馈
  addShotComment(id, data) {
    const commentData = {
      shot: id,
      content: data.content
    }
    
    // 如果有附件数据，添加到请求中
    if (data.attachment_data) {
      commentData.attachment_data = data.attachment_data
    }
    
    return apiClient.post(`/comments/comments/`, commentData)
  },
  
  // 更新反馈状态（标记为已解决/未解决）
  updateComment(commentId, data) {
    return apiClient.patch(`/comments/comments/${commentId}/`, data)
  },
  
  // 删除反馈
  deleteComment(commentId) {
    return apiClient.delete(`/comments/comments/${commentId}/`)
  }
} 