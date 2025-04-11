from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

class Shot(models.Model):
    """镜头模型，存储镜头基本信息"""
    
    STATUS_CHOICES = [
        ('waiting', _('等待开始')),
        ('in_progress', _('正在制作')),
        ('submit_review', _('提交内审')),
        ('revising', _('正在修改')),
        ('internal_approved', _('内审通过')),
        ('client_review', _('客户审核')),
        ('client_rejected', _('客户退回')),
        ('client_approved', _('客户通过')),
        ('client_revision', _('客户返修')),
        ('deleted_merged', _('已删除或合并')),
        ('suspended', _('暂停制作')),
        ('completed', _('已完结'))
    ]
    
    STAGE_CHOICES = [
        ('LAY', _('Layout')),
        ('BLK', _('Block')),
        ('ANI', _('Animation')),
        ('PASS', _('Pass'))
    ]
    
    DEPARTMENT_CHOICES = [
        ('DH', _('动画')),
        ('JS', _('解算')),
        ('HQ', _('后期'))
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='shots',
        verbose_name=_('所属项目')
    )
    shot_code = models.CharField(_('镜头编号'), max_length=100)
    department = models.CharField(_('所属部门'), max_length=2, choices=DEPARTMENT_CHOICES, default='DH')
    prom_stage = models.CharField(_('推进阶段'), max_length=4, choices=STAGE_CHOICES, default='LAY')
    status = models.CharField(_('制作状态'), max_length=20, choices=STATUS_CHOICES, default='waiting')
    artist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_shots', verbose_name=_('制作者'))
    duration_frame = models.IntegerField(_('时长(帧)'), default=0)
    deadline = models.DateField(_('截止日期'), null=True, blank=True)
    last_submit_date = models.DateField(_('最近提交日期'), null=True, blank=True)
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
        indexes = [
            models.Index(fields=['shot_code']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['deadline']),
        ]
        
    def __str__(self):
        return f"{self.project.code} - {self.shot_code}"


class ShotNote(models.Model):
    """镜头备注模型，存储镜头备注信息"""
    
    shot = models.ForeignKey(Shot, on_delete=models.CASCADE, related_name='notes', verbose_name=_('镜头'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shot_notes', verbose_name=_('添加人'))
    content = models.TextField(_('备注内容'))
    is_important = models.BooleanField(_('重要提示'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('镜头备注')
        verbose_name_plural = _('镜头备注')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Note for {self.shot.shot_code} by {self.user.username}" 