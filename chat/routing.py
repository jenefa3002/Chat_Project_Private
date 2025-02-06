from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from . import consumers
from .consumers import UserStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<sender_username>\w+)/(?P<recipient_username>\w+)/$', consumers.PrivateChatConsumer.as_asgi(), name='chat'),
    re_path(r'ws/screenshare/$', consumers.ScreenShareConsumer.as_asgi()),
    re_path(r'ws/status/', UserStatusConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),

]
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
               websocket_urlpatterns
            )
        ),
    }
)