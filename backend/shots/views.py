from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shot
from .serializers import ShotSerializer, ShotListSerializer
from projects.models import Project

class ShotViewSet(viewsets.ModelViewSet):
    """
    镜头视图集，处理镜头相关的API请求
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'project']
    search_fields = ['shot_code', 'description']
    ordering_fields = ['shot_code', 'status', 'deadline', 'created_at', 'updated_at']
    ordering = ['shot_code']
    
    def get_queryset(self):
        """根据查询参数过滤镜头"""
        queryset = Shot.objects.all()
        
        # 按项目代号过滤
        project_code = self.request.query_params.get('project_code', None)
        if project_code:
            queryset = queryset.filter(project__code=project_code)
            
        # 按状态过滤
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # 按期限过滤
        is_overdue = self.request.query_params.get('is_overdue', None)
        if is_overdue and is_overdue.lower() == 'true':
            from django.utils import timezone
            today = timezone.now().date()
            queryset = queryset.filter(deadline__lt=today, status__in=['in_progress', 'review', 'need_revision'])
            
        return queryset
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return ShotListSerializer
        return ShotSerializer
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """快速更新镜头状态的接口"""
        shot = self.get_object()
        status = request.data.get('status', None)
        
        if not status:
            return Response({'error': '状态不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status not in dict(Shot.STATUS_CHOICES).keys():
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
            
        shot.status = status
        shot.save()
        
        serializer = self.get_serializer(shot)
        return Response(serializer.data)
        
    def perform_create(self, serializer):
        """创建镜头时的额外操作"""
        # 可以在这里添加创建镜头时的额外逻辑
        serializer.save()
        
    def perform_update(self, serializer):
        """更新镜头时的额外操作"""
        # 可以在这里添加状态变更的日志记录等逻辑
        serializer.save() 