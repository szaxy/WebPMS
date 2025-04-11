from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserListSerializer, CustomTokenObtainPairSerializer,
    UserRegistrationSerializer, UserApprovalSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义Token视图，使用自定义的Token序列化器"""
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集，处理用户相关的API请求
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'approve_user':
            return UserApprovalSerializer
        return UserSerializer
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'approve_user', 'pending_approvals']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """根据用户角色和部门过滤查询集"""
        queryset = User.objects.all()
        
        # 系统管理员可以查看所有用户
        if self.request.user.is_admin:
            return queryset
            
        # 主管可以查看同部门所有用户
        if self.request.user.is_supervisor:
            return queryset.filter(department=self.request.user.department)
            
        # 带片可以查看同部门所有用户
        if self.request.user.is_leader:
            return queryset.filter(department=self.request.user.department)
            
        # 其他用户只能查看同部门且已审核通过的用户
        return queryset.filter(
            department=self.request.user.department,
            registration_status='approved'
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """更新当前用户信息"""
        # 普通用户不能修改自己的角色和审核状态
        data = request.data.copy()
        if not request.user.is_admin:
            if 'role' in data:
                data.pop('role')
            if 'registration_status' in data:
                data.pop('registration_status')
        
        serializer = UserSerializer(
            request.user, 
            data=data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """获取待审核的用户列表"""
        pending_users = User.objects.filter(registration_status='pending')
        serializer = UserListSerializer(pending_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_user(self, request, pk=None):
        """审核用户注册"""
        user = self.get_object()
        serializer = UserApprovalSerializer(
            user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 