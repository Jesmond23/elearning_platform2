from rest_framework import serializers
from .models import PrivateMessage, ChatNotification
from accounts.models import CustomUser


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_picture']


#To test retrieval and display of message
class PrivateMessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer()
    receiver = UserMiniSerializer()

    class Meta:
        model = PrivateMessage
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'room_name']


#To test notification
class ChatNotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer()

    class Meta:
        model = ChatNotification
        fields = ['id', 'sender', 'message', 'timestamp', 'is_read']


#To test api to send message
class PrivateMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ['receiver', 'content', 'room_name']  # sender is set in the view