from rest_framework import serializers
from .models import Shot
from projects.models import Project

class ShotSerializer(serializers.ModelSerializer):
    """镜头序列化器，用于API数据交换"""
    
    project_name = serializers.ReadOnlyField(source='project.name')
    project_code = serializers.ReadOnlyField(source='project.code')
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'project_name', 'project_code', 
            'shot_code', 'prom_stage', 'status', 'deadline', 
            'duration_frame', 'description', 'metadata',
            'cgtw_task_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ShotListSerializer(serializers.ModelSerializer):
    """镜头列表序列化器，用于列表显示，包含较少字段"""
    
    project_code = serializers.ReadOnlyField(source='project.code')
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'project_code', 'shot_code',
            'status', 'deadline', 'updated_at'
        ] 