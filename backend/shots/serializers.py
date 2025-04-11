from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shot, ShotNote
from projects.serializers import ProjectSerializer
from users.serializers import UserSerializer

User = get_user_model()

class ShotNoteSerializer(serializers.ModelSerializer):
    """镜头备注序列化器"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )
    
    class Meta:
        model = ShotNote
        fields = [
            'id', 'shot', 'user', 'user_id', 'content', 
            'is_important', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def create(self, validated_data):
        # 确保当前用户是备注的创建者
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ShotListSerializer(serializers.ModelSerializer):
    """镜头列表序列化器，用于显示镜头列表"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    artist_name = serializers.CharField(source='artist.username', read_only=True)
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'project_name', 'shot_code', 
            'prom_stage', 'status', 'artist', 'artist_name',
            'deadline', 'last_submit_date', 'duration_frame'
        ]

class ShotDetailSerializer(serializers.ModelSerializer):
    """镜头详情序列化器，用于显示镜头详情"""
    project = ProjectSerializer(read_only=True)
    artist = UserSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='artist',
        required=False,
        allow_null=True
    )
    notes = ShotNoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shot
        fields = [
            'id', 'project', 'shot_code', 'prom_stage', 'status',
            'deadline', 'last_submit_date', 'duration_frame', 
            'description', 'metadata', 'artist', 'artist_id',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ShotBulkUpdateSerializer(serializers.Serializer):
    """批量更新镜头序列化器"""
    shot_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    prom_stage = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    status = serializers.ChoiceField(
        choices=Shot.STATUS_CHOICES,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

class ShotRenameRuleSerializer(serializers.Serializer):
    """镜头重命名规则序列化器"""
    shot_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    prefix = serializers.CharField(required=True)
    suffix = serializers.CharField(required=False, allow_blank=True, default='')
    start_number = serializers.IntegerField(required=True, min_value=1)
    # 下面两个字段二选一
    end_number = serializers.IntegerField(required=False, allow_null=True)
    count = serializers.IntegerField(required=False, allow_null=True)
    # 步长
    step = serializers.IntegerField(required=False, default=10, min_value=1)
    # 数字位数
    digits = serializers.IntegerField(required=False, default=4, min_value=1)
    
    def validate(self, data):
        """验证end_number和count至少提供一个"""
        if not data.get('end_number') and not data.get('count'):
            raise serializers.ValidationError("必须提供end_number或count其中之一")
        return data 