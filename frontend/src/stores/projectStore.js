import { defineStore } from 'pinia'
import projectService from '../services/projectService'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref([])
  const currentProject = ref(null)
  const projectStats = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const activeProjects = computed(() => 
    projects.value.filter(p => p.status === 'in_progress')
  )
  
  const archivedProjects = computed(() => 
    projects.value.filter(p => p.status === 'archived')
  )
  
  const projectsCount = computed(() => projects.value.length)
  
  // 操作
  async function fetchProjects() {
    try {
      loading.value = true
      error.value = null
      
      console.log('正在获取项目列表...')
      const response = await projectService.getProjects()
      console.log('项目API响应:', response)
      
      // 处理可能的分页和非分页响应
      if (response.data && response.data.results && Array.isArray(response.data.results)) {
        // 处理分页响应
        console.log('检测到分页响应，共有', response.data.count, '个项目')
        projects.value = response.data.results
      } else if (Array.isArray(response.data)) {
        // 处理非分页响应（数组）
        console.log('检测到非分页响应，共有', response.data.length, '个项目')
        projects.value = response.data
      } else {
        // 处理意外响应
        console.error('意外的响应格式:', response.data)
        projects.value = []
      }
      
      // 检查结果的有效性
      const validProjects = projects.value.filter(p => p && typeof p === 'object' && p.id)
      if (validProjects.length !== projects.value.length) {
        console.warn('存在无效的项目数据，过滤前:', projects.value.length, '过滤后:', validProjects.length)
        projects.value = validProjects
      }
      
      return projects.value
    } catch (err) {
      console.error('Error fetching projects:', err)
      if (err.response) {
        console.error('错误状态:', err.response.status)
        console.error('错误数据:', err.response.data)
      }
      error.value = '获取项目列表失败'
      projects.value = []
      return []
    } finally {
      loading.value = false
    }
  }
  
  async function fetchProject(id) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.getProject(id)
      currentProject.value = response.data
      
      return currentProject.value
    } catch (err) {
      console.error(`Error fetching project ${id}:`, err)
      error.value = '获取项目详情失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function createProject(projectData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.createProject(projectData)
      const newProject = response.data
      
      // 更新本地状态
      projects.value.push(newProject)
      
      return newProject
    } catch (err) {
      console.error('Error creating project:', err)
      error.value = '创建项目失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function updateProject(id, projectData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.updateProject(id, projectData)
      const updatedProject = response.data
      
      // 更新本地状态
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = updatedProject
      }
      
      return updatedProject
    } catch (err) {
      console.error(`Error updating project ${id}:`, err)
      error.value = '更新项目失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function updateProjectStatus(id, status) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.updateProjectStatus(id, status)
      const updatedProject = response.data
      
      // 更新本地状态
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = updatedProject
      }
      
      return updatedProject
    } catch (err) {
      console.error(`Error updating project status ${id}:`, err)
      error.value = '更新项目状态失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function fetchProjectStats(id) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.getProjectStats(id)
      projectStats.value = response.data
      
      return projectStats.value
    } catch (err) {
      console.error(`Error fetching project stats ${id}:`, err)
      error.value = '获取项目统计数据失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function fetchProjectStatistics(id) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.getProjectStatistics(id)
      return response.data
    } catch (err) {
      console.error(`Error fetching project statistics ${id}:`, err)
      error.value = '获取项目统计信息失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function deleteProject(id) {
    try {
      loading.value = true
      error.value = null
      
      await projectService.deleteProject(id)
      
      // 更新本地状态
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value.splice(index, 1)
      }
      
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = null
      }
      
      return true
    } catch (err) {
      console.error(`Error deleting project ${id}:`, err)
      error.value = '删除项目失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function batchDeleteProjects(ids) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.batchDeleteProjects(ids)
      
      // 更新本地状态
      projects.value = projects.value.filter(p => !ids.includes(p.id))
      
      if (currentProject.value && ids.includes(currentProject.value.id)) {
        currentProject.value = null
      }
      
      return response.data
    } catch (err) {
      console.error('Error batch deleting projects:', err)
      error.value = '批量删除项目失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function batchUpdateProjectStatus(ids, status) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.batchUpdateProjectStatus(ids, status)
      
      // 更新本地状态
      ids.forEach(id => {
        const index = projects.value.findIndex(p => p.id === id)
        if (index !== -1) {
          projects.value[index].status = status
        }
      })
      
      if (currentProject.value && ids.includes(currentProject.value.id)) {
        currentProject.value.status = status
      }
      
      return response.data
    } catch (err) {
      console.error('Error batch updating project status:', err)
      error.value = '批量更新项目状态失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function addDepartmentToProject(projectId, department) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.addDepartmentToProject(projectId, department)
      const updatedProject = response.data
      
      // 更新本地状态
      const index = projects.value.findIndex(p => p.id === projectId)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      
      if (currentProject.value && currentProject.value.id === projectId) {
        currentProject.value = updatedProject
      }
      
      return updatedProject
    } catch (err) {
      console.error(`Error adding department to project ${projectId}:`, err)
      error.value = '添加部门失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  async function removeDepartmentFromProject(projectId, department) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.removeDepartmentFromProject(projectId, department)
      const updatedProject = response.data
      
      // 更新本地状态
      const index = projects.value.findIndex(p => p.id === projectId)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      
      if (currentProject.value && currentProject.value.id === projectId) {
        currentProject.value = updatedProject
      }
      
      return updatedProject
    } catch (err) {
      console.error(`Error removing department from project ${projectId}:`, err)
      error.value = '移除部门失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    projects,
    currentProject,
    projectStats,
    loading,
    error,
    // 计算属性
    activeProjects,
    archivedProjects,
    projectsCount,
    // 操作
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    updateProjectStatus,
    fetchProjectStats,
    fetchProjectStatistics,
    deleteProject,
    batchDeleteProjects,
    batchUpdateProjectStatus,
    addDepartmentToProject,
    removeDepartmentFromProject
  }
}) 