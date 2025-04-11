from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型，扩展Django内置的User模型"""
    
    ROLE_CHOICES = (
        ('admin', _('系统管理员')),
        ('supervisor', _('主管')),
        ('leader', _('带片')),
        ('producer', _('制片')),
        ('artist', _('艺术家')),
    )
    
    DEPARTMENT_CHOICES = (
        ('animation', _('动画')),
        ('post', _('后期')),
        ('fx', _('解算')),
        ('producer', _('制片')),
        ('model', _('模型')),
    )
    
    REGISTRATION_STATUS_CHOICES = (
        ('pending', _('待审核')),
        ('approved', _('已批准')),
        ('rejected', _('已拒绝')),
    )
    
    role = models.CharField(_('角色'), max_length=20, choices=ROLE_CHOICES, default='artist')
    department = models.CharField(_('部门'), max_length=20, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    cgtw_id = models.CharField(_('CGTeamwork用户ID'), max_length=100, null=True, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', null=True, blank=True)
    registration_status = models.CharField(_('注册状态'), max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users', verbose_name=_('审批人'))
    approval_date = models.DateTimeField(_('审批时间'), null=True, blank=True)
    registration_notes = models.TextField(_('注册备注'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        
    def __str__(self):
        return self.username
        
    @property
    def is_admin(self):
        return self.role == 'admin'
        
    @property
    def is_supervisor(self):
        return self.role == 'supervisor'
        
    @property
    def is_leader(self):
        return self.role == 'leader'
        
    @property
    def is_producer(self):
        return self.role == 'producer'
        
    @property
    def is_artist(self):
        return self.role == 'artist'
    
    @property
    def is_approved(self):
        return self.registration_status == 'approved'
    
    @property
    def is_pending(self):
        return self.registration_status == 'pending'
    
    @property
    def is_rejected(self):
        return self.registration_status == 'rejected' 