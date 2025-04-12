import { useAuthStore } from '@/stores/authStore'
import { computed } from 'vue'

/**
 * 权限组合式API，提供权限相关的计算属性和方法
 * 使用示例:
 * ```
 * const { canEditShot, canFilterByDepartment } = usePermissions()
 * const isEditable = canEditShot(shotData).value
 * ```
 */
export function usePermissions() {
  const authStore = useAuthStore()

  // 确保初始化权限服务
  if (!authStore.permissionService) {
    authStore.init()
  }

  return {
    // 角色检查
    hasRole: (role) => computed(() => authStore.hasRole(role)),
    hasMinimumRole: (minRole) => computed(() => authStore.hasMinimumRole(minRole)),
    
    // 部门检查
    isDepartment: (dept) => computed(() => authStore.isDepartment(dept)),
    isInDepartments: (deptList) => computed(() => authStore.isInDepartments(deptList)),
    
    // 功能权限
    canFilterByDepartment: computed(() => authStore.canFilterByDepartment()),
    canViewAllShots: computed(() => authStore.canViewAllShots()),
    canEditShot: (shot) => computed(() => authStore.canEditShot(shot)),
    canDeleteShot: computed(() => authStore.canDeleteShot()),
    canManageUsers: computed(() => authStore.canManageUsers()),
    canApproveRegistration: computed(() => authStore.canApproveRegistration()),
    canCreateProject: computed(() => authStore.canCreateProject()),
    canEditProject: (project) => computed(() => authStore.canEditProject(project)),
    
    // 帮助方法
    canAccessShotsByDepartment: computed(() => authStore.canAccessShotsByDepartment()),
    
    // 用户信息
    currentUserRole: computed(() => authStore.user?.role),
    currentUserDepartment: computed(() => authStore.user?.department),
    isAuthenticated: computed(() => authStore.isAuthenticated)
  }
} 