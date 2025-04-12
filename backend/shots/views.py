from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shot, ShotNote
from .serializers import (
    ShotSerializer, ShotListSerializer, 
    ShotNoteSerializer, ShotNoteCreateSerializer
)
from projects.models import Project
from django.utils import timezone

class ShotViewSet(viewsets.ModelViewSet):
    """
    镜头视图集，处理镜头相关的API请求
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'project', 'department', 'prom_stage']
    search_fields = ['shot_code', 'description']
    ordering_fields = ['shot_code', 'status', 'deadline', 'created_at', 'updated_at', 'last_submit_date']
    ordering = ['shot_code']
    
    def get_queryset(self):
        """根据查询参数和用户权限过滤镜头"""
        user = self.request.user
        
        # 系统管理员和制片可以看到所有部门的镜头
        if user.role in ['admin', 'producer']:
            queryset = Shot.objects.all()
        else:
            # 其他角色只能看到自己部门的镜头
            if not user.department:
                return Shot.objects.none()
            
            queryset = Shot.objects.filter(department=user.department)
        
        # 按项目代号过滤
        project_code = self.request.query_params.get('project_code', None)
        if project_code:
            queryset = queryset.filter(project__code=project_code)
        
        # 按项目ID过滤
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        # 按状态过滤
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # 按部门过滤
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
        
        # 按推进阶段过滤
        prom_stage = self.request.query_params.get('prom_stage', None)
        if prom_stage:
            queryset = queryset.filter(prom_stage=prom_stage)
        
        # 按制作者过滤
        artist_id = self.request.query_params.get('artist_id', None)
        if artist_id:
            queryset = queryset.filter(artist_id=artist_id)
            
        # 按期限过滤
        is_overdue = self.request.query_params.get('is_overdue', None)
        if is_overdue and is_overdue.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(deadline__lt=today, status__in=['waiting', 'in_progress', 'revising'])
        
        # 关键词搜索
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(shot_code__icontains=search) | 
                Q(description__icontains=search)
            )
            
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
        status_value = request.data.get('status', None)
        
        if not status_value:
            return Response({'error': '状态不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status_value not in dict(Shot.STATUS_CHOICES).keys():
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果状态变为提交内审且有重要备注，需要在返回数据中提示
        important_notes = []
        if status_value == 'submit_review':
            important_notes = list(shot.notes.filter(is_important=True).values('content', 'user__username', 'created_at'))
        
        # 更新状态
        shot.status = status_value
        
        # 如果状态是提交内审，更新最近提交日期
        if status_value == 'submit_review':
            shot.last_submit_date = timezone.now().date()
            
        shot.save()
        
        serializer = self.get_serializer(shot)
        response_data = serializer.data
        
        if important_notes:
            response_data['important_notes'] = important_notes
            
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新镜头信息"""
        shot_ids = request.data.get('ids', [])
        fields = request.data.get('fields', {})
        
        if not shot_ids:
            return Response({'error': '未指定镜头IDs'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not fields:
            return Response({'error': '未指定要更新的字段'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户有权限访问的镜头
        queryset = self.get_queryset().filter(id__in=shot_ids)
        
        # 检查是否所有镜头都有访问权限
        if len(queryset) != len(shot_ids):
            return Response({'error': '包含无权限访问的镜头'}, status=status.HTTP_403_FORBIDDEN)
        
        # 更新镜头
        update_count = queryset.update(**fields)
        
        return Response({
            'message': f'成功更新{update_count}个镜头',
            'updated_count': update_count
        })
    
    @action(detail=False, methods=['post'])
    def batch_rename(self, request):
        """批量重命名镜头"""
        shot_ids = request.data.get('ids', [])
        prefix = request.data.get('prefix', '')
        suffix = request.data.get('suffix', '')
        start_num = request.data.get('start_num', 10)
        step = request.data.get('step', 10)
        digit_count = request.data.get('digit_count', 4)
        
        if not shot_ids:
            return Response({'error': '未指定镜头IDs'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户有权限访问的镜头
        queryset = self.get_queryset().filter(id__in=shot_ids)
        
        # 检查是否所有镜头都有访问权限
        if len(queryset) != len(shot_ids):
            return Response({'error': '包含无权限访问的镜头'}, status=status.HTTP_403_FORBIDDEN)
        
        # 批量重命名
        renamed_shots = []
        num = start_num
        
        for shot in queryset:
            new_code = f"{prefix}{str(num).zfill(digit_count)}{suffix}"
            shot.shot_code = new_code
            shot.save()
            renamed_shots.append({
                'id': shot.id,
                'old_code': shot.shot_code,
                'new_code': new_code
            })
            num += step
        
        return Response({
            'message': f'成功重命名{len(renamed_shots)}个镜头',
            'renamed_shots': renamed_shots
        })
        
    def perform_create(self, serializer):
        """创建镜头时的额外操作"""
        # 可以在这里添加创建镜头时的额外逻辑
        serializer.save()
        
    def perform_update(self, serializer):
        """更新镜头时的额外操作"""
        # 如果状态更新为提交内审，更新最近提交日期
        if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'submit_review':
            serializer.validated_data['last_submit_date'] = timezone.now().date()
            
        serializer.save()
        
    def destroy(self, request, *args, **kwargs):
        """删除镜头的方法"""
        print(f"接收到删除请求: {request.path}, 参数: {kwargs}")
        try:
            # 获取对象
            instance = self.get_object()
            shot_code = instance.shot_code
            shot_id = instance.id
            
            print(f"准备删除镜头 ID: {shot_id}, 编号: {shot_code}")
            
            # 执行删除
            self.perform_destroy(instance)
            
            print(f"镜头删除成功: {shot_id}")
            
            return Response({
                'message': f'成功删除镜头 {shot_code}',
                'id': shot_id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"删除镜头失败: {str(e)}")
            return Response({
                'error': f'删除镜头失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def perform_destroy(self, instance):
        """执行镜头删除操作"""
        # 可以在这里添加删除前的额外逻辑，比如权限检查等
        instance.delete()

class ShotNoteViewSet(viewsets.ModelViewSet):
    """
    镜头备注视图集，处理镜头备注相关的API请求
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShotNoteSerializer
    filterset_fields = ['shot', 'user', 'is_important']
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤镜头备注"""
        user = self.request.user
        
        # 系统管理员和制片可以看到所有部门的镜头备注
        if user.role in ['admin', 'producer']:
            return ShotNote.objects.all()
        else:
            # 其他角色只能看到自己部门的镜头备注
            if not user.department:
                return ShotNote.objects.none()
            
            return ShotNote.objects.filter(shot__department=user.department)
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'create':
            return ShotNoteCreateSerializer
        return ShotNoteSerializer
    
    @action(detail=False, methods=['get'])
    def shot_notes(self, request):
        """获取指定镜头的备注"""
        shot_id = request.query_params.get('shot_id', None)
        
        if not shot_id:
            return Response({'error': '未指定镜头ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        notes = self.get_queryset().filter(shot_id=shot_id)
        serializer = self.get_serializer(notes, many=True)
        
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """创建备注时的额外操作"""
        shot_id = self.kwargs.get('shot_pk')
        if not shot_id:
            shot_id = self.request.data.get('shot')
            
        serializer.save(
            shot_id=shot_id,
            user=self.request.user
        ) 