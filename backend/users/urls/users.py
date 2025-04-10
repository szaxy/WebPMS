from django.urls import path
from rest_framework.routers import DefaultRouter

# 后续会添加用户视图
# from ..views import UserViewSet

router = DefaultRouter()
# router.register('', UserViewSet, basename='user')

urlpatterns = [
    # path('me/', CurrentUserView.as_view(), name='current_user'),
]

urlpatterns += router.urls 