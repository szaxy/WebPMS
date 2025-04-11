from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShotViewSet, ShotNoteViewSet

# 后续会添加镜头视图
# from .views import ShotViewSet

# 为先根据URL解析确保我们的自定义路由优先匹配

# 创建路由器
router = DefaultRouter()
router.register(r'shots', ShotViewSet, basename='shot')
router.register(r'shot-notes', ShotNoteViewSet, basename='shot-note')

# 自定义路由
custom_urls = [
    # 更明确的列表URL，确保优先与其他路由匹配
    path('list/', ShotViewSet.as_view({'get': 'list'}), name='shot-list-explicit'),
    path('batch-update/', ShotViewSet.as_view({'post': 'batch_update'}), name='shot-batch-update'),
    path('batch-rename/', ShotViewSet.as_view({'post': 'batch_rename'}), name='shot-batch-rename'),
]

# 注册额外的路由
shot_note_urls = [
    path('<int:pk>/notes/', ShotNoteViewSet.as_view({'get': 'shot_notes'}), name='shot-notes'),
]

# 合并URL模式
urlpatterns = [
    # 首先包含标准DRF路由
    path('', include(router.urls)),
    # 然后匹配自定义路由
    path('shots/', include(custom_urls)),
    # 最后匹配依赖于shots的子路由
    path('shots/', include(shot_note_urls)),
] 