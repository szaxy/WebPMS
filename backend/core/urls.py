from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API文档视图
schema_view = get_schema_view(
    openapi.Info(
        title="WebPMS API",
        default_version='v1',
        description="荷和年动画项目管理平台API文档",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API端点
    path('api/auth/', include('users.urls.auth')),
    path('api/users/', include('users.urls.users')),
    path('api/projects/', include('projects.urls')),
    path('api/', include('shots.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/sync/', include('integrations.cgtw.urls')),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 