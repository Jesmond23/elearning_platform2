from django.shortcuts import render, get_object_or_404
from chat.models import ChatNotification
from courses.models import Course
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from .models import ChatNotification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Message

# Create your views here.
@login_required
def course_chat_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'chat/standalone_chat.html', {'course': course})


@login_required
def private_chat(request, user_id):
    other_user = get_object_or_404(CustomUser, id = user_id)

    if other_user == request.user:
        #Redirect if error
        return render(request,'chat/private_chat_invalid.html')
    

    #Mark notifications as read
    ChatNotification.objects.filter(sender = other_user, recipient = request.user, is_read = False).update(is_read = True)


    return render(request,'chat/private_chat.html',{
        'other_user': other_user
    })


@login_required
def chat_notifications_view(request):
    notifications = request.user.chat_notifications.order_by('-timestamp')
    request.user.chat_notifications.filter(is_read = False).update(is_read = True)

    return render(request, 'chat/chat_notifications.html',{
        'notifications':notifications
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_private_message(request):
    recipient_id = request.data.get('receiver')
    content = request.data.get('content')

    if not recipient_id or not content:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        recipient = CustomUser.objects.get(id=recipient_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)

    Message.objects.create(sender=request.user, receiver=recipient, content=content)
    return Response({'message': 'Message sent'}, status=status.HTTP_201_CREATED)