from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
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
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_shots',
        verbose_name=_('制作者')
    )
    last_submit_date = models.DateField(_('最近提交日期'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('镜头')
        verbose_name_plural = _('镜头')
        ordering = ['shot_code']
        unique_together = ['project', 'shot_code']
        
    def __str__(self):
        return f"{self.project.code} - {self.shot_code}"
        
    @property
    def department_prefix(self):
        """根据镜头编号获取部门前缀"""
        if self.shot_code.startswith('DH_'):
            return 'animation'  # 动画部门
        elif self.shot_code.startswith('JS_'):
            return 'fx'  # 解算部门
        elif self.shot_code.startswith('HQ_'):
            return 'post'  # 后期部门
        return None


class ShotNote(models.Model):
    """镜头备注模型，用于存储镜头的重要提示等信息"""
    
    shot = models.ForeignKey(
        Shot, 
        on_delete=models.CASCADE, 
        related_name='notes',
        verbose_name=_('关联镜头')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='shot_notes',
        verbose_name=_('添加人')
    )
    content = models.TextField(_('备注内容'))
    is_important = models.BooleanField(_('是否重要提示'), default=False, 
                                      help_text=_('如果标记为重要，当制作人提交镜头时会收到提醒'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('镜头备注')
        verbose_name_plural = _('镜头备注')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.shot.shot_code} - {self.created_at.strftime('%Y-%m-%d')}" 