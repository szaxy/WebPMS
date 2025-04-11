from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Comment, Attachment, UserMention
from .serializers import CommentSerializer, AttachmentSerializer
from shots.models import Shot

class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集，处理评论相关的API请求
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据查询参数过滤评论"""
        queryset = Comment.objects.all()
        
        # 按镜头过滤
        shot_id = self.request.query_params.get('shot', None)
        if shot_id:
            queryset = queryset.filter(shot_id=shot_id)
            
        # 只显示顶级评论
        is_top_level = self.request.query_params.get('top_level', None)
        if is_top_level and is_top_level.lower() == 'true':
            queryset = queryset.filter(reply_to__isnull=True)
            
        # 按解决状态过滤
        is_resolved = self.request.query_params.get('is_resolved', None)
        if is_resolved is not None:
            is_resolved_bool = is_resolved.lower() == 'true'
            queryset = queryset.filter(is_resolved=is_resolved_bool)
            
        return queryset
    
    def perform_create(self, serializer):
        """创建评论时自动设置当前用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """标记评论为已解决/未解决"""
        comment = self.get_object()
        is_resolved = request.data.get('is_resolved', True)
        
        comment.is_resolved = is_resolved
        comment.save()
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """获取评论的所有回复"""
        comment = self.get_object()
        replies = Comment.objects.filter(reply_to=comment)
        
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)

class AttachmentViewSet(viewsets.ModelViewSet):
    """
    附件视图集，处理附件上传和管理
    """
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def get_queryset(self):
        return Attachment.objects.all()
    
    def perform_create(self, serializer):
        """创建附件时关联到评论"""
        comment_id = self.request.data.get('comment')
        
        try:
            comment = Comment.objects.get(id=comment_id)
            
            # 确保当前用户是评论的创建者
            if comment.user != self.request.user:
                raise PermissionError("您没有权限为此评论添加附件")
                
            serializer.save(comment=comment)
            
        except Comment.DoesNotExist:
            raise ValueError("评论不存在") 