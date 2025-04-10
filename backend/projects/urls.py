from django.urls import path
from rest_framework.routers import DefaultRouter

# 后续会添加项目视图
# from .views import ProjectViewSet

router = DefaultRouter()
# router.register('', ProjectViewSet, basename='project')

urlpatterns = []

urlpatterns += router.urls 