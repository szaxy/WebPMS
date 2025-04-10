from django.db import models
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    """项目模型，存储项目基本信息"""
    
    STATUS_CHOICES = (
        ('in_progress', _('进行中')),
        ('paused', _('已暂停')),
        ('archived', _('已归档')),
    )
    
    name = models.CharField(_('项目名称'), max_length=200)
    code = models.CharField(_('项目代号'), max_length=50, unique=True)
    status = models.CharField(_('项目状态'), max_length=20, choices=STATUS_CHOICES, default='in_progress')
    start_date = models.DateField(_('开始日期'), null=True, blank=True)
    recsubmit_date = models.DateField(_('最近提交日期'), null=True, blank=True)
    end_date = models.DateField(_('结束日期'), null=True, blank=True)
    description = models.TextField(_('项目描述'), null=True, blank=True)
    cgtw_project_id = models.CharField(_('CGTeamwork项目ID'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('项目')
        verbose_name_plural = _('项目')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.code})" 