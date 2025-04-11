from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShotViewSet, ShotNoteViewSet

# 后续会添加镜头视图
# from .views import ShotViewSet

router = DefaultRouter()
router.register(r'shots', ShotViewSet, basename='shot')
router.register(r'shot-notes', ShotNoteViewSet, basename='shot-note')

urlpatterns = [
    path('', include(router.urls)),
] 