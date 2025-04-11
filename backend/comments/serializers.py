from rest_framework import serializers
from .models import Comment, Attachment, UserMention
from django.contrib.auth import get_user_model

User = get_user_model()

class AttachmentSerializer(serializers.ModelSerializer):
    """附件序列化器"""
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'file_path', 'file_name', 
            'file_size', 'mime_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class UserMentionSerializer(serializers.ModelSerializer):
    """用户提及序列化器"""
    
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = UserMention
        fields = ['id', 'user', 'username', 'is_read']
        read_only_fields = ['id']

class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    
    user_username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    mentions = UserMentionSerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'shot', 'user', 'user_username', 'user_avatar',
            'content', 'timestamp', 'is_resolved', 'reply_to',
            'attachments', 'mentions', 'replies_count'
        ]
        read_only_fields = ['id', 'timestamp', 'user', 'user_username', 'user_avatar']
    
    def get_replies_count(self, obj):
        """获取回复数量"""
        return obj.replies.count()
    
    def create(self, validated_data):
        """创建评论时处理附件和@提及"""
        # 获取当前用户
        validated_data['user'] = self.context['request'].user
        
        # 创建评论
        comment = Comment.objects.create(**validated_data)
        
        # 处理附件
        attachments_data = self.context['request'].data.get('attachments', [])
        for attachment_data in attachments_data:
            Attachment.objects.create(comment=comment, **attachment_data)
        
        # 处理@提及 (解析评论内容中的@用户名)
        content = validated_data.get('content', '')
        import re
        mentioned_usernames = re.findall(r'@(\w+)', content)
        
        for username in mentioned_usernames:
            try:
                user = User.objects.get(username=username)
                UserMention.objects.create(comment=comment, user=user)
            except User.DoesNotExist:
                pass
        
        return comment 