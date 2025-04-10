from django.urls import path
from rest_framework.routers import DefaultRouter

# 后续会添加反馈视图
# from .views import CommentViewSet

router = DefaultRouter()
# router.register('', CommentViewSet, basename='comment')

urlpatterns = []

urlpatterns += router.urls 