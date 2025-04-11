from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, AttachmentViewSet

# 后续会添加反馈视图
# from .views import CommentViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')
router.register('attachments', AttachmentViewSet, basename='attachment')

urlpatterns = []

urlpatterns += router.urls 