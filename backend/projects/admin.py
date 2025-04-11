from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Project, ProjectDepartment

class ProjectDepartmentInline(admin.TabularInline):
    """项目部门关联内联管理"""
    model = ProjectDepartment
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """项目管理界面"""
    list_display = ('name', 'code', 'status', 'start_date', 'end_date', 'get_departments_display')
    list_filter = ('status', 'project_departments__department')
    search_fields = ('name', 'code', 'description')
    inlines = [ProjectDepartmentInline]
    
    def get_departments_display(self, obj):
        """获取部门列表显示"""
        departments = obj.get_departments()
        dept_names = [dict(ProjectDepartment.DEPARTMENT_CHOICES).get(dept, dept) for dept in departments]
        return ", ".join(dept_names) if dept_names else "-"
    get_departments_display.short_description = _('关联部门')

@admin.register(ProjectDepartment)
class ProjectDepartmentAdmin(admin.ModelAdmin):
    """项目部门关联管理界面"""
    list_display = ('project', 'department', 'get_department_display')
    list_filter = ('department',)
    search_fields = ('project__name', 'project__code')
    
    def get_department_display(self, obj):
        """获取部门显示名称"""
        return obj.get_department_display()
    get_department_display.short_description = _('部门名称') 