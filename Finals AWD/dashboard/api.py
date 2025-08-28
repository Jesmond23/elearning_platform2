from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dashboard.models import Notification
from .serializers import UserSerializer, NotificationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications_api(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)