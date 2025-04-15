from rest_framework import serializers
from .models import Shot, ShotNote, ShotNoteAttachment
from projects.models import Project
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

class ShotSerializer(serializers.ModelSerializer):
    """镜头序列化器，用于API数据交换"""
    
    project_name = serializers.ReadOnlyField(source='project.name')
    project_code = serializers.ReadOnlyField(source='project.code')
    artist_name = serializers.ReadOnlyField(source='artist.username', allow_null=True)
    department_display = serializers.ReadOnlyField(source='get_department_display')
    prom_stage_display = serializers.ReadOnlyField(source='get_prom_stage_display')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'project_name', 'project_code', 
            'shot_code', 'department', 'department_display', 
            'prom_stage', 'prom_stage_display', 'status', 'status_display', 
            'artist', 'artist_name', 'deadline', 'last_submit_date',
            'duration_frame', 'framepersecond', 'description', 'metadata',
            'cgtw_task_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ShotListSerializer(serializers.ModelSerializer):
    """镜头列表序列化器，用于列表显示，包含较少字段"""
    
    project_code = serializers.ReadOnlyField(source='project.code')
    artist_name = serializers.ReadOnlyField(source='artist.username', allow_null=True)
    department_display = serializers.ReadOnlyField(source='get_department_display')
    prom_stage_display = serializers.ReadOnlyField(source='get_prom_stage_display')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    notes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'project_code', 'shot_code',
            'department', 'department_display', 
            'prom_stage', 'prom_stage_display',
            'status', 'status_display', 'artist', 'artist_name',
            'deadline', 'last_submit_date', 'duration_frame', 'framepersecond',
            'notes_count', 'updated_at'
        ]
    
    def get_notes_count(self, obj):
        return obj.notes.count()

class ShotNoteAttachmentSerializer(serializers.ModelSerializer):
    """镜头备注附件序列化器"""
    
    file_content = serializers.CharField(write_only=True, required=False)
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = ShotNoteAttachment
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
                    file_name = f"note_clipboard_{uuid.uuid4().hex}{ext}"
                    
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
                        attachment = ShotNoteAttachment(
                            note=validated_data['note'],
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
            attachment = ShotNoteAttachment(
                note=validated_data['note'],
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

class ShotNoteSerializer(serializers.ModelSerializer):
    """镜头备注序列化器，用于API数据交换"""
    
    user_name = serializers.ReadOnlyField(source='user.username')
    attachments = ShotNoteAttachmentSerializer(many=True, read_only=True)
    attachment_data = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = ShotNote
        fields = [
            'id', 'shot', 'user', 'user_name', 
            'content', 'is_important', 'attachments', 'attachment_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ShotNoteCreateSerializer(serializers.ModelSerializer):
    """镜头备注创建序列化器，用于创建镜头备注"""
    
    attachment_data = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = ShotNote
        fields = ['content', 'is_important', 'attachment_data']
    
    def create(self, validated_data):
        """创建备注并处理附件"""
        # 提取附件数据
        attachment_data = validated_data.pop('attachment_data', [])
        
        shot_id = self.context['shot_id']
        user = self.context['request'].user
        
        shot = Shot.objects.get(id=shot_id)
        
        note = ShotNote.objects.create(
            shot=shot,
            user=user,
            **validated_data
        )
        
        # 处理附件
        attachment_serializer = ShotNoteAttachmentSerializer()
        for attachment in attachment_data:
            # 确保添加note引用
            attachment['note'] = note
            attachment_serializer.create(attachment)
        
        return note 