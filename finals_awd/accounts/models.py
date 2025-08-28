from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default = False)
    is_student = models.BooleanField(default = False)
    profile_picture = models.ImageField(upload_to='profiles/',
                                        null=True, blank=True)
    bio = models.TextField(blank = True)

    @property
    def notifications(self):
        return self.chat_notifications.all()

    def __str__(self):
        return self.username
