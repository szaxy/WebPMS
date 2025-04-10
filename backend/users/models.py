from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型，扩展Django内置的User模型"""
    
    ROLE_CHOICES = (
        ('admin', _('系统管理员')),
        ('manager', _('管理员')),
        ('artist', _('艺术家')),
    )
    
    DEPARTMENT_CHOICES = (
        ('animation', _('动画')),
        ('post', _('后期')),
        ('fx', _('解算')),
        ('producer', _('制片')),
    )
    
    role = models.CharField(_('角色'), max_length=20, choices=ROLE_CHOICES, default='artist')
    department = models.CharField(_('部门'), max_length=20, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    cgtw_id = models.CharField(_('CGTeamwork用户ID'), max_length=100, null=True, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        
    def __str__(self):
        return self.username
        
    @property
    def is_admin(self):
        return self.role == 'admin'
        
    @property
    def is_manager(self):
        return self.role == 'manager'
        
    @property
    def is_artist(self):
        return self.role == 'artist' 