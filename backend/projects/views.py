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
        
        # 系统管理员和超级用户可以查看所有项目
        if user.is_admin or user.is_superuser:
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
        if department_param and (user.is_admin or user.is_superuser):  # 只有管理员可以跨部门查看
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