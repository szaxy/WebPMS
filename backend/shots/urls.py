from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShotViewSet, ShotNoteViewSet, ShotNoteAttachmentViewSet

# 后续会添加镜头视图
# from .views import ShotViewSet

# 为先根据URL解析确保我们的自定义路由优先匹配

# 创建路由器
router = DefaultRouter()
router.register(r'shots', ShotViewSet, basename='shot')
router.register(r'shot-notes', ShotNoteViewSet, basename='shot-note')
router.register(r'shot-note-attachments', ShotNoteAttachmentViewSet, basename='shot-note-attachment')

# 合并URL模式
urlpatterns = [
    # 让DefaultRouter处理所有标准和@action路由
    path('', include(router.urls)),
] 