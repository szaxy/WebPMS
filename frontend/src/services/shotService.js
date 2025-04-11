import axios from 'axios'
import { useTokenInterceptor } from '@/utils/tokenInterceptor'

// 创建axios实例并应用token拦截器
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
})
useTokenInterceptor(apiClient)

const shotService = {
  /**
   * 获取镜头列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getShots(params = {}) {
    return apiClient.get('/shots/', { params })
  },
  
  /**
   * 从API返回的URL获取shots资源
   * @param {String} url - 完整的shots资源URL
   * @returns {Promise}
   */
  getShotsFromURL(url, params = {}) {
    // 如果URL已经是完整URL，直接使用它，否则拼接baseURL
    if (url.startsWith('http')) {
      return apiClient.get(url, { params })
    } else {
      // 移除baseURL前缀(如果URL已包含)，避免重复
      const baseURL = apiClient.defaults.baseURL;
      let cleanedUrl = url;
      if (baseURL && url.startsWith(baseURL)) {
        cleanedUrl = url.substring(baseURL.length);
      }
      // 移除开头的斜杠，避免与baseURL重复
      if (cleanedUrl.startsWith('/')) {
        cleanedUrl = cleanedUrl.substring(1);
      }
      return apiClient.get(cleanedUrl, { params });
    }
  },
  
  /**
   * 获取镜头详情
   * @param {Number} id - 镜头ID
   * @returns {Promise}
   */
  getShotById(id) {
    return apiClient.get(`/shots/${id}/`)
  },
  
  /**
   * 创建新镜头
   * @param {Object} shotData - 镜头数据
   * @returns {Promise}
   */
  createShot(shotData) {
    return apiClient.post('/shots/', shotData)
  },
  
  /**
   * 更新镜头
   * @param {Number} id - 镜头ID
   * @param {Object} shotData - 镜头更新数据
   * @returns {Promise}
   */
  updateShot(id, shotData) {
    return apiClient.patch(`/shots/${id}/`, shotData)
  },
  
  /**
   * 删除镜头
   * @param {Number} id - 镜头ID
   * @returns {Promise}
   */
  deleteShot(id) {
    return apiClient.delete(`/shots/${id}/`)
  },
  
  /**
   * 批量更新镜头
   * @param {Object} updateData - 包含shot_ids和更新字段的数据
   * @returns {Promise}
   */
  bulkUpdateShots(updateData) {
    return apiClient.post('/shots/bulk_update/', updateData)
  },
  
  /**
   * 批量重命名镜头
   * @param {Object} renameData - 包含重命名规则的数据
   * @returns {Promise}
   */
  bulkRenameShots(renameData) {
    return apiClient.post('/shots/bulk_rename/', renameData)
  },
  
  /**
   * 提交镜头（并检查重要备注）
   * @param {Number} id - 镜头ID
   * @returns {Promise}
   */
  submitShot(id) {
    return apiClient.post(`/shots/${id}/submit/`)
  },
  
  /**
   * 获取镜头备注列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getShotNotes(params = {}) {
    return apiClient.get('/shot-notes/', { params })
  },
  
  /**
   * 添加镜头备注
   * @param {Object} noteData - 备注数据
   * @returns {Promise}
   */
  createShotNote(noteData) {
    return apiClient.post('/shot-notes/', noteData)
  },
  
  /**
   * 更新镜头备注
   * @param {Number} id - 备注ID
   * @param {Object} noteData - 备注更新数据
   * @returns {Promise}
   */
  updateShotNote(id, noteData) {
    return apiClient.patch(`/shot-notes/${id}/`, noteData)
  },
  
  /**
   * 删除镜头备注
   * @param {Number} id - 备注ID
   * @returns {Promise}
   */
  deleteShotNote(id) {
    return apiClient.delete(`/shot-notes/${id}/`)
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

export default shotService