from django.urls import path
from channels.routing import URLRouter

# 导入我们将创建的WebSocket Consumer
# 目前先注释掉，等消费者实现后再取消注释
# from shots.consumers import ShotConsumer

websocket_urlpatterns = [
    # 项目消息通道
    # path('ws/projects/<str:project_id>/', ShotConsumer.as_asgi()),
] 