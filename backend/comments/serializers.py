from rest_framework import serializers
from .models import Comment, Attachment, UserMention
from django.contrib.auth import get_user_model
import mimetypes
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import uuid
import base64
import re

User = get_user_model()

class AttachmentSerializer(serializers.ModelSerializer):
    """附件序列化器"""
    
    file_content = serializers.CharField(write_only=True, required=False)
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'file_path', 'thumbnail_path', 'file_name', 
            'file_size', 'mime_type', 'is_image', 'created_at',
            'file_content', 'file'
        ]
        read_only_fields = ['id', 'file_path', 'thumbnail_path', 'file_size', 'mime_type', 'is_image', 'created_at']
    
    def create(self, validated_data):
        """处理附件创建"""
        file_content = validated_data.pop('file_content', None)
        file = validated_data.pop('file', None)
        
        if not file_content and not file:
            raise serializers.ValidationError("必须提供文件内容或文件对象")
        
        if file_content:
            # 处理Base64编码的文件内容（剪贴板粘贴）
            # 匹配data:开头的数据URI
            if file_content.startswith('data:'):
                # 提取MIME类型和编码数据
                content_pattern = re.compile(r'data:(.+?);base64,(.+)')
                match = content_pattern.match(file_content)
                if match:
                    mime_type = match.group(1)
                    file_data = base64.b64decode(match.group(2))
                    
                    # 生成文件名
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    file_name = f"clipboard_{uuid.uuid4().hex}{ext}"
                    
                    # 创建内存文件对象
                    file_obj = io.BytesIO(file_data)
                    
                    # 如果是图片，创建缩略图
                    if mime_type.startswith('image/'):
                        is_image = True
                        # 创建图片对象并生成缩略图
                        image = Image.open(file_obj)
                        image.thumbnail((200, 200))
                        thumb_io = io.BytesIO()
                        image.save(thumb_io, format=image.format or 'JPEG')
                        thumb_io.seek(0)
                        
                        # 创建缩略图文件
                        thumb_file = InMemoryUploadedFile(
                            thumb_io,
                            'thumbnail',
                            f"thumb_{file_name}",
                            mime_type,
                            thumb_io.getbuffer().nbytes,
                            None
                        )
                        
                        # 创建原始文件对象
                        file_obj.seek(0)
                        memory_file = InMemoryUploadedFile(
                            file_obj,
                            'file',
                            file_name,
                            mime_type,
                            len(file_data),
                            None
                        )
                        
                        # 创建附件对象
                        attachment = Attachment(
                            comment=validated_data['comment'],
                            file_name=file_name,
                            file_size=len(file_data),
                            mime_type=mime_type,
                            is_image=is_image
                        )
                        attachment.file_path.save(file_name, memory_file, save=False)
                        attachment.thumbnail_path.save(f"thumb_{file_name}", thumb_file, save=False)
                        attachment.save()
                        return attachment
            
            raise serializers.ValidationError("无效的文件内容格式")
            
        elif file:
            # 处理直接上传的文件
            file_name = file.name
            file_size = file.size
            mime_type = file.content_type or mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
            is_image = mime_type.startswith('image/')
            
            # 创建附件对象
            attachment = Attachment(
                comment=validated_data['comment'],
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                is_image=is_image
            )
            
            # 保存文件
            attachment.file_path.save(file_name, file, save=False)
            
            # 如果是图片，创建缩略图
            if is_image:
                image = Image.open(file)
                image.thumbnail((200, 200))
                thumb_io = io.BytesIO()
                image.save(thumb_io, format=image.format or 'JPEG')
                thumb_io.seek(0)
                
                thumb_file = InMemoryUploadedFile(
                    thumb_io,
                    'thumbnail',
                    f"thumb_{file_name}",
                    mime_type,
                    thumb_io.getbuffer().nbytes,
                    None
                )
                
                attachment.thumbnail_path.save(f"thumb_{file_name}", thumb_file, save=False)
                
            attachment.save()
            return attachment
        
        return None

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
    attachment_data = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Comment
        fields = [
            'id', 'shot', 'user', 'user_username', 'user_avatar',
            'content', 'timestamp', 'is_resolved', 'reply_to',
            'attachments', 'mentions', 'replies_count', 'attachment_data'
        ]
        read_only_fields = ['id', 'timestamp', 'user', 'user_username', 'user_avatar']
    
    def get_replies_count(self, obj):
        """获取回复数量"""
        return obj.replies.count()
    
    def create(self, validated_data):
        """创建评论时处理附件和@提及"""
        # 提取附件数据
        attachment_data = validated_data.pop('attachment_data', [])
        
        # 获取当前用户
        validated_data['user'] = self.context['request'].user
        
        # 创建评论
        comment = Comment.objects.create(**validated_data)
        
        # 处理附件
        attachment_serializer = AttachmentSerializer()
        for attachment in attachment_data:
            # 确保添加comment引用
            attachment['comment'] = comment
            attachment_serializer.create(attachment)
        
        # 处理@提及 (解析评论内容中的@用户名)
        content = validated_data.get('content', '')
        mentioned_usernames = re.findall(r'@(\w+)', content)
        
        for username in mentioned_usernames:
            try:
                user = User.objects.get(username=username)
                UserMention.objects.create(comment=comment, user=user)
            except User.DoesNotExist:
                pass
        
        return comment 