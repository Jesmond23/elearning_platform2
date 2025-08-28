from django.urls import path, include

from .views import course_chat_view, chat_notifications_view
from . import views
from .api import private_chat_messages_api,chat_notifications_api, send_private_message


urlpatterns = [
    path('course/<int:course_id>/', course_chat_view, name='course_chat'),

    path('chat/<int:user_id>/', views.private_chat, name='private_chat'),

    path('notifications/', chat_notifications_view, name='chat_notifications'),

    #API for chat messages
    path('api/private_messages/', private_chat_messages_api, name='private_chat_messages_api'),

    #API for chat notifications
    path('api/chat_notifications/', chat_notifications_api, name='chat_notifications_api'),

    #API for sending messages
    path('api/private-messages/send/', send_private_message, name='send_private_message'),

    #Server side test
]
