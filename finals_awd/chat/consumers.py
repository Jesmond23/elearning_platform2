import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import CustomUser
from .models import Message, PrivateMessage
from courses.models import Course
from channels.db import database_sync_to_async

from .models import PrivateMessage, ChatNotification

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connect attempt started")
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.course_id}'

        user = self.scope['user']
        course = await database_sync_to_async(Course.objects.get)(id=self.course_id)

        #Ensure only user is allowed(enrolled student/teacher)
        if not await self.is_user_in_course(user, course):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        messages = await self.get_last_messages(course.id)
        for msg in messages:
            username = await self.get_username(msg)
            timestamp = await self.get_timestamp(msg)
            profile_pic = await self.get_profile_pic(msg)
            await self.send(text_data = json.dumps({
                'username': username,
                'message' : msg.content,
                'timestamp': timestamp,
                'profile_pic': profile_pic
            }))

    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self,text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']

        await self.save_message(self.course_id, sender,message)
        timestamp = await self.get_latest_timestamp(sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': sender.username,
                'message': message,
                'timestamp': timestamp,
                'profile_pic': self.get_full_profile_pic_url(sender)

            }
        )

    async def chat_message(self,event):
        await self.send(text_data = json.dumps({
            'username': event['username'],
            'message':event['message'],
            'timestamp': event['timestamp'],
            'profile_pic': event['profile_pic'],
        }))

    @database_sync_to_async
    def get_last_messages(self,course_id):
        return Message.objects.filter(course_id=course_id).order_by('-timestamp')[:20][::-1]
    
    @database_sync_to_async
    def save_message(self, course_id, sender, message):
        try:
            course = Course.objects.get(id=course_id)
            return Message.objects.create(course=course, sender=sender, content=message)
        except Exception as e:
            print("save_message error:", e)
            raise

    @database_sync_to_async
    def is_user_in_course(self, user, course):
        return user == course.teacher or course.enrollments.filter(student=user).exists()
    
    @database_sync_to_async
    def get_username(self, msg):
        return msg.sender.username
    
    @database_sync_to_async
    def get_timestamp(self, msg):
        return msg.timestamp.strftime('%H:%M')

    @database_sync_to_async
    def get_latest_timestamp(self, sender):
        msg = Message.objects.filter(sender=sender).latest('timestamp')
        return msg.timestamp.strftime('%H:%M')

    @database_sync_to_async
    def get_profile_pic(self, msg):
        return self.get_full_profile_pic_url(msg.sender)

    

    #Fetch a fresh version of the image instead of a stale/cache image for WebSocket
    def get_full_profile_pic_url(self, user):
        if user.profile_picture:
            scheme = self.scope.get("scheme", "http")
            host_header = dict(self.scope["headers"]).get(b"host", b"localhost:8000").decode()
            return f"{scheme}://{host_header}{user.profile_picture.url}?v={int(datetime.datetime.utcnow().timestamp())}"
        return "/static/default-avatar.png"


    

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.user = self.scope['user']

        #Ensure only two users
        if not self.user.is_authenticated:
            await self.close()
            return
        
        ids = sorted([str(self.user.id), str(self.other_user_id)])
        self.room_group_name = f'private_chat_{ids[0]}_{ids[1]}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_previous_messages(self.user.id, self.other_user_id)

        for msg in messages:

            profile_pic = self.get_full_profile_pic_url(msg.sender)

            await self.send(text_data=json.dumps({
                'sender': msg.sender.username,
                'message': msg.content,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'profile_pic' : profile_pic,
            }))

    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_id = self.other_user_id
        sender = self.user

        await self.save_message(sender.id, receiver_id,message)

        timestamp = datetime.datetime.now().strftime('%H:%M')
        profile_pic = self.get_full_profile_pic_url(sender)



        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'sender': self.user.username,
                'timestamp': timestamp,
                'profile_pic' : profile_pic
            }
        )

    async def chat_message(self, event):
        await self.send(text_data = json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'profile_pic' : event['profile_pic']
        }))

    
    @database_sync_to_async
    def save_message(self,sender_id, receiver_id, content):
        sender = CustomUser.objects.get(id=sender_id)
        receiver = CustomUser.objects.get(id=receiver_id)
        
        ids=sorted([str(sender_id), str(receiver_id)])
        room_name = f'private_chat_{ids[0]}_{ids[1]}'
        
        PrivateMessage.objects.create(
            sender=sender,receiver = receiver,
            content = content,
            room_name = room_name)
        # Create notification for receiver
        if sender != receiver:
            ChatNotification.objects.create(
                recipient=receiver,
                sender=sender,
                message=content
            )
    
    @database_sync_to_async
    def get_previous_messages(self, user1_id, user2_id):
        ids = sorted([str(user1_id), str(user2_id)])
        room_name = f'private_chat_{ids[0]}_{ids[1]}'
        return list(
            PrivateMessage.objects
            .filter(room_name=room_name)
            #preload sender object
            .select_related('sender')
            .order_by('timestamp')[:50]
        )
    
    #Fetch a fresh version of the image instead of a stale/cache image for WebSocket
    def get_full_profile_pic_url(self, user):
        if user.profile_picture:
            scheme = self.scope.get("scheme", "http")
            host_header = dict(self.scope["headers"]).get(b"host", b"localhost:8000").decode()
            return f"{scheme}://{host_header}{user.profile_picture.url}?v={int(datetime.datetime.utcnow().timestamp())}"
        return "/static/default-avatar.png"

    
    