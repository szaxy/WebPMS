from rest_framework import serializers
from .models import Shot, ShotNote
from projects.models import Project
from django.contrib.auth import get_user_model

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

class ShotNoteSerializer(serializers.ModelSerializer):
    """镜头备注序列化器，用于API数据交换"""
    
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ShotNote
        fields = [
            'id', 'shot', 'user', 'user_name', 
            'content', 'is_important', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ShotNoteCreateSerializer(serializers.ModelSerializer):
    """镜头备注创建序列化器，用于创建镜头备注"""
    
    class Meta:
        model = ShotNote
        fields = ['content', 'is_important']
    
    def create(self, validated_data):
        shot_id = self.context['shot_id']
        user = self.context['request'].user
        
        shot = Shot.objects.get(id=shot_id)
        
        note = ShotNote.objects.create(
            shot=shot,
            user=user,
            **validated_data
        )
        
        return note 