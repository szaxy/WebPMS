from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Shot, ShotNote
from .serializers import (
    ShotListSerializer, 
    ShotDetailSerializer, 
    ShotNoteSerializer,
    ShotBulkUpdateSerializer,
    ShotRenameRuleSerializer
)
from projects.models import Project

class ShotViewSet(viewsets.ModelViewSet):
    """
    镜头视图集，处理镜头相关的API请求
    """
    queryset = Shot.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'prom_stage', 'artist']
    search_fields = ['shot_code', 'description']
    ordering_fields = ['shot_code', 'status', 'deadline', 'last_submit_date', 'created_at', 'updated_at']
    ordering = ['shot_code']
    
    def get_serializer_class(self):
        """根据不同的操作返回不同的序列化器"""
        if self.action == 'list':
            return ShotListSerializer
        elif self.action in ['bulk_update', 'bulk_rename']:
            return ShotBulkUpdateSerializer
        else:
            return ShotDetailSerializer
    
    def get_queryset(self):
        """
        根据用户部门过滤镜头
        - 系统管理员和制片部门可以查看所有镜头
        - 其他部门只能查看自己部门的镜头
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 超级用户可以查看所有
        if user.is_superuser:
            return queryset
        
        # 判断是否有department参数，如果有且用户有权限，按参数过滤
        department = self.request.query_params.get('department')
        if department and (user.is_admin or user.is_superuser or user.department == 'producer'):
            if department == 'animation':
                return queryset.filter(shot_code__startswith='DH_')
            elif department == 'fx':
                return queryset.filter(shot_code__startswith='JS_')
            elif department == 'post':
                return queryset.filter(shot_code__startswith='HQ_')
            return queryset
        
        # 没有department参数或没有权限，按用户部门过滤
        if user.is_admin or user.is_superuser or user.department == 'producer':
            # 管理员和制片可以查看所有
            return queryset
        elif user.department == 'animation':
            # 动画部门只能看DH_开头的
            return queryset.filter(shot_code__startswith='DH_')
        elif user.department == 'fx':
            # 解算部门只能看JS_开头的
            return queryset.filter(shot_code__startswith='JS_')
        elif user.department == 'post':
            # 后期部门只能看HQ_开头的
            return queryset.filter(shot_code__startswith='HQ_')
        
        # 用户没有设置部门，但如果是管理员仍然可以访问所有镜头
        if user.is_admin or user.is_superuser:
            return queryset
            
        # 其他情况（如部门为空且非管理员）
        return queryset.none()
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新镜头状态、推进阶段、制作者"""
        serializer = ShotBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            shot_ids = serializer.validated_data.pop('shot_ids')
            update_data = {k: v for k, v in serializer.validated_data.items() if v is not None}
            
            # 获取用户可见的镜头
            visible_shots = self.get_queryset().filter(id__in=shot_ids)
            if not visible_shots:
                return Response({"detail": "未找到可更新的镜头"}, status=status.HTTP_404_NOT_FOUND)
            
            # 批量更新
            visible_shots.update(**update_data)
            return Response({"detail": f"成功更新{visible_shots.count()}个镜头"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_rename(self, request):
        """批量重命名镜头"""
        serializer = ShotRenameRuleSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            shot_ids = data['shot_ids']
            prefix = data['prefix']
            suffix = data['suffix']
            start_number = data['start_number']
            step = data['step']
            digits = data['digits']
            
            # 计算序列长度
            if data.get('end_number'):
                end_number = data['end_number']
                numbers = list(range(start_number, end_number + 1, step))
            else:
                count = data['count']
                numbers = [start_number + i * step for i in range(count)]
            
            # 获取用户可见的镜头并按ID排序
            shots = list(self.get_queryset().filter(id__in=shot_ids).order_by('id'))
            
            if not shots:
                return Response({"detail": "未找到可重命名的镜头"}, status=status.HTTP_404_NOT_FOUND)
            
            # 如果序列长度与镜头数量不匹配，给出警告
            warning = None
            if len(numbers) != len(shots):
                warning = f"警告：序列长度({len(numbers)})与所选镜头数量({len(shots)})不匹配"
                # 取较小的长度
                rename_count = min(len(numbers), len(shots))
            else:
                rename_count = len(shots)
            
            # 执行重命名
            for i in range(rename_count):
                number_str = str(numbers[i]).zfill(digits)
                new_code = f"{prefix}{number_str}{suffix}"
                shots[i].shot_code = new_code
                shots[i].save()
            
            response_data = {"detail": f"成功重命名{rename_count}个镜头"}
            if warning:
                response_data["warning"] = warning
            
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交镜头，将状态改为review并检查重要备注"""
        shot = self.get_object()
        
        # 检查是否有重要备注
        important_notes = shot.notes.filter(is_important=True)
        
        if important_notes.exists():
            # 返回重要备注信息，但不自动更改状态
            notes_data = ShotNoteSerializer(important_notes, many=True).data
            return Response({
                "detail": "镜头存在重要备注，请确认后再提交",
                "important_notes": notes_data
            }, status=status.HTTP_200_OK)
        
        # 没有重要备注，直接更改状态
        shot.status = 'review'
        shot.last_submit_date = timezone.now().date()
        shot.save()
        
        return Response({"detail": "镜头已成功提交"}, status=status.HTTP_200_OK)

class ShotNoteViewSet(viewsets.ModelViewSet):
    """镜头备注视图集"""
    serializer_class = ShotNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """按镜头过滤备注"""
        return ShotNote.objects.all()
    
    def perform_create(self, serializer):
        """创建备注时自动关联当前用户"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """更新镜头时的额外操作"""
        # 可以在这里添加状态变更的日志记录等逻辑
        serializer.save() 