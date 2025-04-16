from rest_framework import viewsets, filters, status, parsers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shot, ShotNote, ShotNoteAttachment
from .serializers import (
    ShotSerializer, ShotListSerializer, 
    ShotNoteSerializer, ShotNoteCreateSerializer,
    ShotNoteAttachmentSerializer
)
from projects.models import Project
from django.utils import timezone

# 定义一个标准分页类，明确允许 page_size 参数
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100 # 如果前端不传 page_size，则默认为 100 (同 settings.py)
    page_size_query_param = 'page_size' # 允许前端通过 'page_size' 参数覆盖
    max_page_size = 1000 # 可选：设置每页最大记录数

class ShotViewSet(viewsets.ModelViewSet):
    """
    镜头视图集，处理镜头相关的API请求
    """
    permission_classes = [IsAuthenticated]
    # 显式设置分页类
    pagination_class = StandardResultsSetPagination
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
        
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """批量创建镜头"""
        shots_data = request.data.get('shots', [])
        
        if not shots_data:
            return Response({'error': '未提供镜头数据'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果shots_data是字典形式的批量生成数据
        if isinstance(shots_data, dict):
            # 解析批量生成参数
            project_id = shots_data.get('project')
            prefix = shots_data.get('prefix', '')
            start_num = shots_data.get('start', 10)
            count = shots_data.get('count', 5)
            digit_count = shots_data.get('digit_count', 3)
            suffix = shots_data.get('suffix', '')
            step = shots_data.get('step', 10)
            
            # 其他共用字段
            common_fields = {k: v for k, v in shots_data.items() 
                           if k not in ['project', 'prefix', 'start', 'count', 'digit_count', 'suffix', 'step']}
            
            # 生成实际的镜头列表数据
            bulk_shots_data = []
            for i in range(count):
                num = start_num + (i * step)
                shot_code = f"{prefix}{str(num).zfill(digit_count)}{suffix}"
                
                shot_data = {
                    'project': project_id,
                    'shot_code': shot_code,
                    **common_fields
                }
                bulk_shots_data.append(shot_data)
                
            shots_data = bulk_shots_data
        
        # 创建序列化器用于验证
        serializer = self.get_serializer(data=shots_data, many=True)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': f'验证失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 高效批量创建
        try:
            shots = serializer.save()
            
            return Response({
                'message': f'成功创建 {len(shots)} 个镜头',
                'created_count': len(shots),
                'created_shots': self.get_serializer(shots, many=True).data
            })
        except Exception as e:
            return Response({'error': f'创建镜头失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除镜头"""
        shot_ids = request.data.get('ids', [])
        
        if not shot_ids:
            return Response({'error': '未指定镜头IDs'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户有权限访问的镜头
        queryset = self.get_queryset().filter(id__in=shot_ids)
        
        # 检查是否所有镜头都有访问权限
        if len(queryset) != len(shot_ids):
            return Response({
                'error': '包含无权限访问的镜头',
                'requested_count': len(shot_ids),
                'accessible_count': len(queryset)
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取镜头编号用于响应
        shot_data = list(queryset.values('id', 'shot_code'))
        
        # 执行批量删除
        deleted_count, _ = queryset.delete()
        
        return Response({
            'message': f'成功删除{deleted_count}个镜头',
            'deleted_count': deleted_count,
            'deleted_shots': shot_data
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
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    
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
        if self.action in ['create', 'with_attachment']:
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
        """创建备注时的额外操作 - 现在主要由 ShotNoteCreateSerializer.create 处理"""
        # 保留此方法以防万一，但主要逻辑移至序列化器
        # 确保 user 在 context 中传递
        if 'user' not in serializer.validated_data:
             serializer.save(user=self.request.user)
        else:
             serializer.save()
    
    @action(detail=False, methods=['post'])
    def with_attachment(self, request):
        """创建带附件的备注"""
        shot_id = request.data.get('shot')
        if not shot_id:
            return Response({'error': '未指定镜头ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取合适的序列化器 (现在会正确返回 ShotNoteCreateSerializer)
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        # 确保 request 在 context 中，以便序列化器访问 request.user
        context['request'] = request 
        context['shot_id'] = shot_id
        
        serializer = serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        
        # 直接调用 serializer.save()，它会调用 ShotNoteCreateSerializer.create
        note = serializer.save() 
        
        # 返回创建的备注，使用 ShotNoteSerializer 以包含完整信息
        response_serializer = ShotNoteSerializer(note, context=context)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class ShotNoteAttachmentViewSet(viewsets.ModelViewSet):
    """
    镜头备注附件视图集，处理备注附件上传和管理
    """
    serializer_class = ShotNoteAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    def get_queryset(self):
        return ShotNoteAttachment.objects.all()
    
    def perform_create(self, serializer):
        """创建附件时关联到备注"""
        note_id = self.request.data.get('note')
        
        try:
            note = ShotNote.objects.get(id=note_id)
            
            # 确保当前用户是备注的创建者
            if note.user != self.request.user:
                raise PermissionError("您没有权限为此备注添加附件")
                
            serializer.save(note=note)
            
        except ShotNote.DoesNotExist:
            raise ValueError("备注不存在")
    
    @action(detail=False, methods=['post'])
    def upload_clipboard(self, request):
        """处理剪贴板粘贴上传的图片"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save()
        
        return Response(
            self.get_serializer(attachment).data,
            status=status.HTTP_201_CREATED
        ) 