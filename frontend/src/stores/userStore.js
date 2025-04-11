import { defineStore } from 'pinia'
import authService from '../services/authService'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 获取用户列表，支持筛选
  async function fetchUsers(params = {}) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.getUsers(params)
      users.value = response.data || []
      
      return response.data
    } catch (err) {
      console.error('Error fetching users:', err)
      error.value = '获取用户列表失败'
      return []
    } finally {
      loading.value = false
    }
  }

  // 获取用户详情
  async function fetchUserById(userId) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.getUser(userId)
      return response.data
    } catch (err) {
      console.error('Error fetching user:', err)
      error.value = '获取用户详情失败'
      return null
    } finally {
      loading.value = false
    }
  }

  // 更新用户信息
  async function updateUser(userId, userData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await authService.updateUser(userId, userData)
      
      // 更新本地缓存
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      console.error('Error updating user:', err)
      error.value = '更新用户信息失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除用户
  async function deleteUser(userId) {
    try {
      loading.value = true
      error.value = null
      
      await authService.deleteUser(userId)
      
      // 从本地缓存中删除
      users.value = users.value.filter(u => u.id !== userId)
      
      return true
    } catch (err) {
      console.error('Error deleting user:', err)
      error.value = '删除用户失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    users,
    loading,
    error,
    // 操作
    fetchUsers,
    fetchUserById,
    updateUser,
    deleteUser
  }
}) 