from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from django.db.models import Q
from .models import PrivateMessage, ChatNotification
from .serializers import PrivateMessageSerializer, ChatNotificationSerializer, PrivateMessageCreateSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def private_chat_messages_api(request):
    messages = PrivateMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')[:50]

    serializer = PrivateMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_notifications_api(request):
    notes = ChatNotification.objects.filter(recipient=request.user).order_by('-timestamp')[:30]
    serializer = ChatNotificationSerializer(notes, many=True)
    return Response(serializer.data)


@extend_schema(
    request=PrivateMessageCreateSerializer,
    responses=PrivateMessageSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_private_message(request):
    serializer = PrivateMessageCreateSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save(sender=request.user)
        return Response(PrivateMessageSerializer(message).data, status=201)
    return Response(serializer.errors, status=400)