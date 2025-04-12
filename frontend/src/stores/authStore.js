import { defineStore } from 'pinia'
import authService from '@/services/authService'
import { ref, computed } from 'vue'
import router from '../router'
import { usePermission } from '@/services/permissionService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    users: [],
    pendingUsers: [],
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    isLoading: false,
    error: null,
    permissionService: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => state.user?.role === 'manager' || state.user?.role === 'admin',
    isProducer: (state) => state.user?.role === 'producer',
    isAnySupervisor: (state) => state.isAdmin || state.isManager || state.user?.role === 'supervisor',
    isLeader: (state) => state.user?.role === 'leader',
    isArtist: (state) => state.user?.role === 'artist',
    department: (state) => state.user?.department || null
  },

  actions: {
    // 初始化方法
    async init() {
      // 初始化权限服务
      this.permissionService = usePermission({
        get user() {
          return useAuthStore().user
        }
      })
      
      // 如果已经有令牌，尝试获取用户信息
      if (this.token && !this.user) {
        try {
          await this.fetchCurrentUser()
          console.log('用户信息初始化成功:', this.user?.username)
        } catch (error) {
          console.error('初始化用户信息失败:', error)
        }
      }
    },
    
    // 登录操作
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.login(credentials)
        this.setTokens(response.data.access, response.data.refresh)
        await this.fetchCurrentUser()
        
        // 登录成功后重定向到Dashboard
        router.push({ name: 'dashboard' })
        
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '登录失败'
        console.error('登录失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 注册操作
    async register(userData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.register(userData)
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '注册失败'
        console.error('注册失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 获取当前用户信息
    async fetchCurrentUser() {
      this.isLoading = true
      try {
        const response = await authService.getCurrentUser()
        this.user = response.data
        return { success: true, data: response.data }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 只有在401/403错误时才清除令牌并登出
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.logout()
        }
        return { success: false, error: error.message }
      } finally {
        this.isLoading = false
      }
    },

    // 获取所有用户
    async fetchUsers(params) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.getUsers(params)
        this.users = response.data
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '获取用户列表失败'
        console.error('获取用户列表失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 获取待审核用户
    async fetchPendingUsers() {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.getPendingUsers()
        this.pendingUsers = response.data
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '获取待审核用户失败'
        console.error('获取待审核用户失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 审核用户
    async approveUser(userId, data) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.approveUser(userId, data)
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '审核用户失败'
        console.error('审核用户失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 更新用户信息
    async updateUser(userId, data) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authService.updateUser(userId, data)
        return { success: true, data: response.data }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '更新用户失败'
        console.error('更新用户失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 删除用户
    async deleteUser(userId) {
      this.isLoading = true
      this.error = null
      try {
        await authService.deleteUser(userId)
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '删除用户失败'
        console.error('删除用户失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 设置认证令牌
    setTokens(accessToken, refreshToken) {
      this.token = accessToken
      this.refreshToken = refreshToken
      localStorage.setItem('token', accessToken)
      localStorage.setItem('refreshToken', refreshToken)
    },

    // 刷新令牌
    async refreshAuthToken() {
      try {
        const response = await authService.refreshToken(this.refreshToken)
        this.setTokens(response.data.access, response.data.refresh || this.refreshToken)
        return { success: true }
      } catch (error) {
        console.error('刷新令牌失败:', error)
        this.logout()
        return { success: false, error: error.message }
      }
    },

    // 注销
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      // 清除其他可能的缓存状态
      
      // 重定向到登录页
      router.push({ name: 'login' })
    },

    async updateProfile(userData) {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await authService.updateCurrentUser(userData)
        this.user = response.data
        return { success: true }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '更新失败'
        console.error('更新个人信息失败:', error)
        return { success: false, error: this.error }
      } finally {
        this.isLoading = false
      }
    },

    // 权限检查方法代理
    hasRole(role) {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.hasRole(role) : false
    },

    hasMinimumRole(minRole) {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.hasMinimumRole(minRole) : false
    },

    isDepartment(dept) {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.isDepartment(dept) : false
    },

    isInDepartments(deptList) {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.isInDepartments(deptList) : false
    },

    canFilterByDepartment() {
      if (!this.permissionService) {
        this.init()
      }
      if (!this.permissionService) return false
      
      try {
        return this.permissionService.canFilterByDepartment()
      } catch (error) {
        console.error('canFilterByDepartment 调用失败:', error)
        // 降级处理：如果方法调用失败，检查是否为管理员或制片
        return this.isAdmin || this.isProducer || 
               (this.user?.department === 'admin') || (this.user?.department === 'producer')
      }
    },

    canViewAllShots() {
      if (!this.permissionService) {
        this.init()
      }
      if (!this.permissionService) return false
      
      try {
        return this.permissionService.canViewAllShots()
      } catch (error) {
        console.error('canViewAllShots 调用失败:', error)
        // 降级处理
        return this.isAdmin || this.isManager || this.isProducer
      }
    },

    canEditShot(shot) {
      if (!this.permissionService) {
        this.init()
      }
      if (!this.permissionService) return false
      
      try {
        return this.permissionService.canEditShot(shot)
      } catch (error) {
        console.error('canEditShot 调用失败:', error)
        // 降级处理
        return this.isAdmin || this.isProducer
      }
    },

    canDeleteShot() {
      if (!this.permissionService) {
        this.init()
      }
      if (!this.permissionService) return false
      
      try {
        return this.permissionService.canDeleteShot()
      } catch (error) {
        console.error('canDeleteShot 调用失败:', error)
        // 降级处理
        return this.isAdmin || this.isProducer
      }
    },

    canManageUsers() {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.canManageUsers() : false
    },

    canApproveRegistration() {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.canApproveRegistration() : false
    },

    canCreateProject() {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.canCreateProject() : false
    },

    canEditProject(project) {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.canEditProject(project) : false
    },

    canAccessShotsByDepartment() {
      if (!this.permissionService) {
        this.init()
      }
      return this.permissionService ? this.permissionService.canAccessShotsByDepartment() : false
    }
  }
}) 