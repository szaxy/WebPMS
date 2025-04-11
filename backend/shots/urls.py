from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ShotViewSet

# 后续会添加镜头视图
# from .views import ShotViewSet

router = DefaultRouter()
router.register('', ShotViewSet, basename='shot')

urlpatterns = []

urlpatterns += router.urls 