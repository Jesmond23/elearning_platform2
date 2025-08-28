from django.db import models
from accounts.models import CustomUser
from courses.models import Course


# Create your models here.

class StatusUpdate(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete = models.CASCADE)
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('assignment_submission', 'Assignment Submission'),
        ('material_upload', 'Material Upload'),
        ('chat', 'Chat'),
        ('course_drop', 'Course Drop'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete= models.CASCADE,
                                  related_name='notifications')
    course = models.ForeignKey(Course,on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"To {self.recipient.username} - {self.message}"
    

class Comment(models.Model):
    status = models.ForeignKey(StatusUpdate, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(CustomUser,on_delete = models.CASCADE,
                               )
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.author.username} on {self.status.id}: {self.content[:30]}"
    