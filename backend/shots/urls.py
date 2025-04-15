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

# 自定义路由
custom_urls = [
    # 更明确的列表URL，确保优先与其他路由匹配
    path('list/', ShotViewSet.as_view({'get': 'list'}), name='shot-list-explicit'),
    # 删除自定义create路径，使用DRF自动生成的标准路由
    path('batch-update/', ShotViewSet.as_view({'post': 'batch_update'}), name='shot-batch-update'),
    path('batch-rename/', ShotViewSet.as_view({'post': 'batch_rename'}), name='shot-batch-rename'),
    # 明确的删除路由 - 将HTTP方法映射到destroy视图
    path('<int:pk>/', ShotViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='shot-detail'),
]

# 注册额外的路由
shot_note_urls = [
    path('<int:pk>/notes/', ShotNoteViewSet.as_view({'get': 'shot_notes'}), name='shot-notes'),
]

# 合并URL模式
urlpatterns = [
    # 首先包含DefaultRouter的路由，确保它们获得优先匹配
    path('', include(router.urls)),
    
    # 直接将自定义路由附加到根路径
    path('shots/<int:pk>/', ShotViewSet.as_view({'delete': 'destroy'}), name='shot-delete-direct'),
    
    # 然后再包含自定义路由
    path('shots/', include(custom_urls)),
    path('shots/', include(shot_note_urls)),
] 