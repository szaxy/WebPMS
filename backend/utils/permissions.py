from rest_framework import permissions

class IsApprovedUser(permissions.BasePermission):
    """检查用户是否已通过审核"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_approved)

class IsAdmin(permissions.BasePermission):
    """检查用户是否是系统管理员"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

class IsSupervisor(permissions.BasePermission):
    """检查用户是否是主管"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_supervisor or request.user.is_admin))
    
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有对象
        if request.user.is_admin:
            return True
            
        # 主管只能访问自己部门的对象
        # 根据对象类型判断部门
        if hasattr(obj, 'department'):
            return obj.department == request.user.department
        elif hasattr(obj, 'project') and hasattr(obj.project, 'get_departments'):
            # 检查对象所属项目是否与用户部门关联
            return request.user.department in obj.project.get_departments()
        return False

class IsLeader(permissions.BasePermission):
    """检查用户是否是带片"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_leader or request.user.is_supervisor or request.user.is_admin))
    
    def has_object_permission(self, request, view, obj):
        # 管理员和主管可以访问所有对象
        if request.user.is_admin or request.user.is_supervisor:
            return True
            
        # 带片只能访问自己部门的对象
        if hasattr(obj, 'department'):
            return obj.department == request.user.department
        elif hasattr(obj, 'project') and hasattr(obj.project, 'get_departments'):
            return request.user.department in obj.project.get_departments()
        return False

class IsInSameDepartment(permissions.BasePermission):
    """检查用户是否与对象属于同一部门"""
    
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有对象
        if request.user.is_admin:
            return True
            
        # 检查用户是否有部门
        if not request.user.department:
            return False
            
        # 根据对象类型判断是否同一部门
        if hasattr(obj, 'department'):
            return obj.department == request.user.department
        elif hasattr(obj, 'project') and hasattr(obj.project, 'get_departments'):
            return request.user.department in obj.project.get_departments()
        elif hasattr(obj, 'user') and hasattr(obj.user, 'department'):
            return obj.user.department == request.user.department
        return False 