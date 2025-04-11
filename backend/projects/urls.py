from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register('', ProjectViewSet, basename='project')

urlpatterns = [
    path('<int:pk>/add-department/', ProjectViewSet.as_view({'post': 'add_department'}), name='project-add-department'),
    path('<int:pk>/remove-department/', ProjectViewSet.as_view({'post': 'remove_department'}), name='project-remove-department'),
]

urlpatterns += router.urls 