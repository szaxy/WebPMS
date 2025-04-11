from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from django.utils import timezone
from django.contrib import messages

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """自定义用户模型的Admin配置"""
    
    list_display = ('username', 'device_code', 'email', 'first_name', 'last_name', 'role', 'department', 'registration_status', 'is_staff')
    list_filter = ('role', 'department', 'registration_status', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'device_code', 'email', 'first_name', 'last_name')
    actions = ['approve_users', 'reject_users']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'device_code', 'avatar')}),
        (_('CGTeamwork信息'), {'fields': ('cgtw_id',)}),
        (_('角色权限'), {'fields': ('role', 'department')}),
        (_('注册审核'), {'fields': ('registration_status', 'registration_notes', 'approved_by', 'approval_date')}),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('approved_by', 'approval_date')
    
    def approve_users(self, request, queryset):
        """批量审核通过用户"""
        updated = queryset.update(
            registration_status='approved',
            approved_by=request.user,
            approval_date=timezone.now()
        )
        self.message_user(request, f'成功批准 {updated} 位用户的注册申请', messages.SUCCESS)
    approve_users.short_description = _('批准选中用户的注册申请')
    
    def reject_users(self, request, queryset):
        """批量拒绝用户"""
        updated = queryset.update(
            registration_status='rejected',
            approved_by=request.user,
            approval_date=timezone.now()
        )
        self.message_user(request, f'已拒绝 {updated} 位用户的注册申请', messages.SUCCESS)
    reject_users.short_description = _('拒绝选中用户的注册申请') 