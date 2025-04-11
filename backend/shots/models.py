from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project

class Shot(models.Model):
    """镜头模型，存储镜头基本信息"""
    
    STATUS_CHOICES = (
        ('in_progress', _('制作中')),
        ('review', _('审核中')),
        ('approved', _('已通过')),
        ('need_revision', _('需修改')),
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='shots',
        verbose_name=_('所属项目')
    )
    shot_code = models.CharField(_('镜头编号'), max_length=100)
    prom_stage = models.CharField(_('推进阶段'), max_length=50, null=True, blank=True)
    status = models.CharField(_('制作状态'), max_length=20, choices=STATUS_CHOICES, default='in_progress')
    deadline = models.DateField(_('截止日期'), null=True, blank=True)
    duration_frame = models.IntegerField(_('时长(帧)'), null=True, blank=True)
    description = models.TextField(_('描述'), null=True, blank=True)
    metadata = models.JSONField(_('元数据'), default=dict, null=True, blank=True)
    cgtw_task_id = models.CharField(_('CGTeamwork任务ID'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('镜头')
        verbose_name_plural = _('镜头')
        ordering = ['shot_code']
        unique_together = ['project', 'shot_code']
        
    def __str__(self):
        return f"{self.project.code} - {self.shot_code}" 