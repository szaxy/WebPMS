/**
 * Token 拦截器
 * 自动为 API 请求添加身份验证 token
 */

/**
 * 为 Axios 实例配置 token 拦截器
 * @param {Object} axiosInstance - Axios 实例
 */
export function useTokenInterceptor(axiosInstance) {
  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config) => {
      // 从 localStorage 获取 token
      const token = localStorage.getItem('token')
      
      // 如果 token 存在，添加到请求头
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器处理 token 过期
  axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      // 如果是 401 Unauthorized 错误，可能是 token 过期
      if (error.response && error.response.status === 401) {
        // 尝试使用刷新 token
        const refreshToken = localStorage.getItem('refreshToken')
        
        // 如果没有刷新 token 或处理失败，清除 token 并重定向到登录页
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        
        // 重定向到登录页
        window.location.href = '/login'
      }
      
      return Promise.reject(error)
    }
  )
} 