from django.db import models
from django.utils.translation import gettext_lazy as _

class SyncLog(models.Model):
    """同步日志表，记录与CGTeamwork的同步操作日志"""
    
    SYNC_TYPE_CHOICES = (
        ('projects', _('项目同步')),
        ('shots', _('镜头同步')),
        ('users', _('用户同步')),
    )
    
    STATUS_CHOICES = (
        ('in_progress', _('进行中')),
        ('success', _('成功')),
        ('failed', _('失败')),
    )
    
    sync_type = models.CharField(_('同步类型'), max_length=50, choices=SYNC_TYPE_CHOICES)
    start_time = models.DateTimeField(_('开始时间'), auto_now_add=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    status = models.CharField(_('同步状态'), max_length=20, choices=STATUS_CHOICES, default='in_progress')
    error_message = models.TextField(_('错误信息'), null=True, blank=True)
    items_synced = models.IntegerField(_('同步条目数'), default=0)
    
    class Meta:
        verbose_name = _('同步日志')
        verbose_name_plural = _('同步日志')
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.start_time.strftime('%Y-%m-%d %H:%M')}" 