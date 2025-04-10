import { defineStore } from 'pinia'
import shotService from '../services/shotService'

export const useShotStore = defineStore('shot', {
  state: () => ({
    shots: [],
    loading: false,
    error: null,
    currentShot: null
  }),
  
  getters: {
    getShotById: (state) => (id) => {
      return state.shots.find(shot => shot.id === id)
    },
    
    shotsByStatus: (state) => (status) => {
      return state.shots.filter(shot => shot.status === status)
    },
    
    totalShots: (state) => state.shots.length,
    
    statusCounts: (state) => {
      const counts = {
        in_progress: 0,
        review: 0,
        approved: 0,
        need_revision: 0
      }
      
      state.shots.forEach(shot => {
        if (counts[shot.status] !== undefined) {
          counts[shot.status]++
        }
      })
      
      return counts
    }
  },
  
  actions: {
    // 加载镜头列表
    async fetchShots(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await shotService.getShots(params)
        this.shots = response.data.results || response.data
        return this.shots
      } catch (error) {
        this.error = error.message || '加载镜头数据失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 加载单个镜头详情
    async fetchShot(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await shotService.getShot(id)
        this.currentShot = response.data
        
        // 更新列表中的对应镜头
        const index = this.shots.findIndex(s => s.id === id)
        if (index > -1) {
          this.shots[index] = response.data
        }
        
        return this.currentShot
      } catch (error) {
        this.error = error.message || '加载镜头详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 创建新镜头
    async createShot(shotData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await shotService.createShot(shotData)
        this.shots.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message || '创建镜头失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 更新镜头
    async updateShot(updatedShot) {
      // 如果只有部分数据，仅更新本地状态
      if (!updatedShot.id) {
        console.error('更新镜头时缺少ID')
        return null
      }
      
      // 更新本地状态
      const index = this.shots.findIndex(s => s.id === updatedShot.id)
      if (index > -1) {
        this.shots[index] = { ...this.shots[index], ...updatedShot }
        
        // 如果是当前镜头，也更新当前镜头
        if (this.currentShot && this.currentShot.id === updatedShot.id) {
          this.currentShot = { ...this.currentShot, ...updatedShot }
        }
        
        return this.shots[index]
      }
      
      return null
    },
    
    // 发送更新到API
    async saveShot(id, shotData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await shotService.updateShot(id, shotData)
        
        // 更新本地状态
        this.updateShot(response.data)
        
        return response.data
      } catch (error) {
        this.error = error.message || '更新镜头失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 删除镜头
    async deleteShot(id) {
      this.loading = true
      this.error = null
      
      try {
        await shotService.deleteShot(id)
        
        // 从列表中移除
        this.shots = this.shots.filter(shot => shot.id !== id)
        
        // 如果是当前镜头，清空当前镜头
        if (this.currentShot && this.currentShot.id === id) {
          this.currentShot = null
        }
        
        return true
      } catch (error) {
        this.error = error.message || '删除镜头失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 重置状态
    resetState() {
      this.shots = []
      this.loading = false
      this.error = null
      this.currentShot = null
    }
  }
}) 