// 角色层级和权限
const ROLE_HIERARCHY = {
  'admin': 100,     // 系统管理员 - 最高权限
  'supervisor': 80, // 主管
  'leader': 60,     // 带片
  'producer': 40,   // 制片
  'artist': 20      // 艺术家 - 最低权限
}

/**
 * 权限服务函数，提供权限检查方法
 * @param {Object} userObj - 包含用户信息的对象或getter
 * @returns {Object} 包含各种权限检查方法的对象
 */
export function usePermission(userObj) {
  // 辅助函数：安全获取用户
  const getUser = () => {
    if (typeof userObj.user === 'function') {
      return userObj.user()
    }
    return userObj.user || null
  }

  return {
    // 用户角色相关权限
    hasRole(role) {
      const user = getUser()
      return user?.role === role
    },
    
    hasMinimumRole(minRole) {
      const user = getUser()
      const userRoleLevel = ROLE_HIERARCHY[user?.role || ''] || 0
      const requiredLevel = ROLE_HIERARCHY[minRole] || 0
      return userRoleLevel >= requiredLevel
    },
    
    // 部门相关权限
    isDepartment(dept) {
      const user = getUser()
      return user?.department === dept
    },

    // 检查用户是否属于多个部门中的任意一个
    isInDepartments(deptList) {
      const user = getUser()
      return deptList.includes(user?.department)
    },
    
    // 特定功能权限
    canFilterByDepartment() {
      const self = this;
      // 管理员和制片可以筛选任何部门
      return self.hasRole('admin') || self.hasRole('producer') || 
             self.isDepartment('admin') || self.isDepartment('producer')
    },
    
    canViewAllShots() {
      const self = this;
      // 管理员、制片和主管可以查看所有镜头
      return self.hasMinimumRole('supervisor') || self.hasRole('producer')
    },
    
    canEditShot(shot) {
      const self = this;
      const user = getUser()
      
      // 管理员可以编辑任何镜头
      if (self.hasRole('admin')) return true
      
      // 制片可以编辑任何镜头
      if (self.hasRole('producer')) return true
      
      // 主管可以编辑所有镜头
      if (self.hasRole('supervisor')) return true
      
      // 带片可以编辑相应部门的镜头
      if (self.hasRole('leader') && self.isDepartment(shot.department)) return true
      
      // 艺术家只能编辑自己的镜头
      if (self.hasRole('artist') && shot.artist === user?.id) return true
      
      return false
    },
    
    canDeleteShot() {
      const self = this;
      // 只有管理员和制片可以删除镜头
      return self.hasRole('admin') || self.hasRole('producer')
    },

    canManageUsers() {
      const self = this;
      // 只有管理员可以管理用户
      return self.hasRole('admin')
    },

    canApproveRegistration() {
      const self = this;
      // 只有管理员可以批准注册
      return self.hasRole('admin')
    },

    canCreateProject() {
      const self = this;
      // 管理员和制片可以创建项目
      return self.hasRole('admin') || self.hasRole('producer')
    },

    canEditProject(project) {
      const self = this;
      // 管理员和制片可以编辑任何项目
      return self.hasRole('admin') || self.hasRole('producer')
    },

    canAccessShotsByDepartment() {
      const self = this;
      const user = getUser()
      
      // 获取当前用户可以查看的部门
      if (self.hasRole('admin') || self.hasRole('producer')) {
        return null // 可以查看所有部门
      }
      return user?.department // 只能查看自己部门
    }
  }
} 