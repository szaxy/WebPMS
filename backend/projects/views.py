from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Project, ProjectDepartment
from .serializers import ProjectSerializer, ProjectListSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目视图集，处理项目相关的API请求
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'status', 'start_date', 'end_date', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限和部门过滤项目"""
        user = self.request.user
        queryset = Project.objects.all()
        
        # 系统管理员可以查看所有项目
        if user.is_admin:
            # 无需过滤，返回所有项目
            pass
        else:
            # 非管理员只能查看与其部门关联的项目
            department = user.department
            if department:
                queryset = queryset.filter(
                    project_departments__department=department
                ).distinct()
            else:
                # 没有部门的用户不能查看任何项目
                queryset = Project.objects.none()
        
        # 按状态过滤
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # 按关键字搜索
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(code__icontains=search) | 
                Q(description__icontains=search)
            )
            
        # 按部门过滤
        department_param = self.request.query_params.get('department', None)
        if department_param and user.is_admin:  # 只有管理员可以跨部门查看
            queryset = queryset.filter(
                project_departments__department=department_param
            ).distinct()
            
        return queryset
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        """创建项目时，如果没有指定部门，默认添加当前用户的部门"""
        data = serializer.validated_data
        
        # 如果没有提供部门列表，且当前用户有部门，则自动添加当前用户部门
        if 'department_ids' not in data and self.request.user.department:
            data['department_ids'] = [self.request.user.department]
            
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def shots(self, request, pk=None):
        """获取项目下的所有镜头"""
        project = self.get_object()
        from shots.models import Shot
        from shots.serializers import ShotListSerializer
        
        shots = Shot.objects.filter(project=project)
        serializer = ShotListSerializer(shots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """快速更新项目状态的接口"""
        project = self.get_object()
        status_value = request.data.get('status', None)
        
        if not status_value:
            return Response({'error': '状态不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status_value not in dict(Project.STATUS_CHOICES).keys():
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
            
        project.status = status_value
        project.save()
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_department(self, request, pk=None):
        """为项目添加部门"""
        project = self.get_object()
        department = request.data.get('department', None)
        
        if not department:
            return Response({'error': '部门不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查部门有效性
        if department not in dict(ProjectDepartment.DEPARTMENT_CHOICES).keys():
            return Response({'error': '无效的部门'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查是否已经关联
        if ProjectDepartment.objects.filter(project=project, department=department).exists():
            return Response({'error': '该部门已关联到此项目'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 创建关联
        ProjectDepartment.objects.create(project=project, department=department)
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_department(self, request, pk=None):
        """从项目中移除部门"""
        project = self.get_object()
        department = request.data.get('department', None)
        
        if not department:
            return Response({'error': '部门不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 查找并删除关联
        try:
            dept_link = ProjectDepartment.objects.get(project=project, department=department)
            dept_link.delete()
        except ProjectDepartment.DoesNotExist:
            return Response({'error': '该部门未关联到此项目'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(project)
        return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除项目"""
        project_ids = request.data.get('ids', [])
        
        if not project_ids:
            return Response({'error': '项目ID列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查权限
        if not request.user.is_admin:
            return Response({'error': '只有管理员可以批量删除项目'}, status=status.HTTP_403_FORBIDDEN)
            
        # 获取项目并检查是否存在
        projects = Project.objects.filter(id__in=project_ids)
        if projects.count() != len(project_ids):
            return Response({'error': '部分项目ID不存在'}, status=status.HTTP_404_NOT_FOUND)
            
        # 执行删除操作
        deleted_count = projects.delete()[0]
        
        return Response({
            'message': f'成功删除{deleted_count}个项目',
            'count': deleted_count
        })
    
    @action(detail=False, methods=['post'])
    def batch_update_status(self, request):
        """批量更新项目状态"""
        project_ids = request.data.get('ids', [])
        status_value = request.data.get('status', None)
        
        if not project_ids:
            return Response({'error': '项目ID列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not status_value:
            return Response({'error': '状态不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status_value not in dict(Project.STATUS_CHOICES).keys():
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取项目并检查是否存在
        projects = Project.objects.filter(id__in=project_ids)
        if projects.count() != len(project_ids):
            return Response({'error': '部分项目ID不存在'}, status=status.HTTP_404_NOT_FOUND)
            
        # 执行更新操作
        updated_count = projects.update(status=status_value)
        
        return Response({
            'message': f'成功更新{updated_count}个项目的状态',
            'count': updated_count
        })
        
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取项目统计信息"""
        project = self.get_object()
        
        # 导入Shot模型
        from shots.models import Shot
        
        # 获取项目下的所有镜头
        shots = Shot.objects.filter(project=project)
        
        # 计算各状态的镜头数量
        status_counts = {}
        for status_code, status_name in Shot.STATUS_CHOICES:
            status_counts[status_code] = shots.filter(status=status_code).count()
            
        # 按部门计算镜头数量
        department_counts = {}
        for dept_code, dept_name in Shot.DEPARTMENT_CHOICES:
            department_counts[dept_code] = shots.filter(department=dept_code).count()
            
        # 计算进度（以完成状态的镜头占比）
        completion_statuses = ['client_approved', 'completed']
        completion_count = shots.filter(status__in=completion_statuses).count()
        total_count = shots.count()
        completion_rate = (completion_count / total_count * 100) if total_count > 0 else 0
            
        # 获取最近更新的镜头
        recent_shots = shots.order_by('-updated_at')[:5].values('id', 'shot_code', 'status', 'updated_at')
        
        # 统计数据组装
        statistics = {
            'shot_count': total_count,
            'status_counts': status_counts,
            'department_counts': department_counts,
            'completion_rate': round(completion_rate, 2),
            'recent_shots': list(recent_shots)
        }
        
        return Response(statistics) 