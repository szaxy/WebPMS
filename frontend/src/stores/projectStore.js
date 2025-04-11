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
      
      const response = await projectService.getProjects()
      
      // 确保数据格式正确
      if (response.data && Array.isArray(response.data.results)) {
        // 分页数据结构
        projects.value = response.data.results
      } else if (response.data && Array.isArray(response.data)) {
        // 直接返回数组
        projects.value = response.data
      } else if (response.data) {
        // 不是预期的数据格式
        console.error('Projects API returned unexpected format:', response.data)
        projects.value = []
      } else {
        // 无数据
        projects.value = []
      }
      
      return projects.value
    } catch (err) {
      console.error('Error fetching projects:', err)
      error.value = '获取项目列表失败'
      projects.value = [] // 确保失败时也设置为空数组
      throw err
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
  
  async function addProject(projectData) {
    try {
      loading.value = true
      error.value = null
      
      const response = await projectService.createProject(projectData)
      const newProject = response.data
      
      // 更新本地状态
      projects.value.push(newProject)
      
      // 重新获取项目列表
      await fetchProjects()
      
      return newProject
    } catch (err) {
      console.error('Error adding project:', err)
      error.value = '添加项目失败'
      throw err
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
    addProject
  }
}) 