
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<course_id>\d+)/$', consumers.ChatConsumer.as_asgi()),

    #private chat
    re_path(r'^ws/private/(?P<user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
]

print("WebSocket routes loaded:", websocket_urlpatterns)
