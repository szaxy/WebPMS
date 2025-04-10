from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from shots.models import Shot

class Comment(models.Model):
    """反馈表，存储对镜头的反馈信息"""
    
    shot = models.ForeignKey(
        Shot, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name=_('关联镜头')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name=_('用户')
    )
    content = models.TextField(_('反馈内容'))
    timestamp = models.DateTimeField(_('时间戳'), auto_now_add=True)
    is_resolved = models.BooleanField(_('是否已解决'), default=False)
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='replies',
        verbose_name=_('回复')
    )
    
    class Meta:
        verbose_name = _('反馈')
        verbose_name_plural = _('反馈')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Attachment(models.Model):
    """附件表，存储反馈的附件信息"""
    
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name=_('关联反馈')
    )
    file_path = models.FileField(_('文件路径'), upload_to='attachments/')
    file_name = models.CharField(_('文件名'), max_length=255)
    file_size = models.PositiveIntegerField(_('文件大小'), help_text=_('文件大小(字节)'))
    mime_type = models.CharField(_('文件类型'), max_length=100)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('附件')
        verbose_name_plural = _('附件')
        
    def __str__(self):
        return self.file_name

class UserMention(models.Model):
    """用户提及表，记录评论中@的用户"""
    
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        related_name='mentions',
        verbose_name=_('关联反馈')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mentions',
        verbose_name=_('用户')
    )
    is_read = models.BooleanField(_('是否已读'), default=False)
    
    class Meta:
        verbose_name = _('用户提及')
        verbose_name_plural = _('用户提及')
        
    def __str__(self):
        return f"{self.comment} - @{self.user.username}" 