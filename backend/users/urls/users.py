from django.urls import path
from rest_framework.routers import DefaultRouter
from ..views import UserViewSet

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('me/', UserViewSet.as_view({'get': 'me', 'patch': 'update_me'}), name='current_user'),
    path('pending-approvals/', UserViewSet.as_view({'get': 'pending_approvals'}), name='pending_approvals'),
    path('<int:pk>/approve/', UserViewSet.as_view({'post': 'approve_user'}), name='approve_user'),
]

urlpatterns += router.urls 