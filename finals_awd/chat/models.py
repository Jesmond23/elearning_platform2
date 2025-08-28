from django.db import models
from accounts.models import CustomUser
from courses.models import Course
# Create your models here.


class Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    
    
class PrivateMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE
                               ,related_name='sent_private_message')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                 related_name='received_private_message')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    #For future retrieval or caching
    room_name = models.CharField(max_length = 100)


    class Meta:
        ordering = ['timestamp']

    
class ChatNotification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  related_name='chat_notifications')
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add = True)
    message = models.TextField(blank = True)


    class Meta:
        ordering = ['-timestamp']
