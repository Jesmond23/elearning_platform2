from django.db import models
from accounts.models import CustomUser
from elearning_platform import settings
# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length = 200)
    description = models.TextField()
    teacher = models.ForeignKey(CustomUser, on_delete = models.CASCADE
                                ,related_name='courses_taught')
    image = models.ImageField(upload_to='course_images/',blank = True,null = True)

    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete = models.CASCADE,
                                related_name='enrollments')
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='enrollments')
    enrolled_on = models.DateTimeField(auto_now_add=True)

class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='materials')
    title = models.CharField(max_length = 255)
    file = models.FileField(upload_to='materials/')
    uploaded_at = models.DateTimeField(auto_now_add = True)

    
class CourseReview(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE,
                               related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        #One review per course per student
        unique_together = ('course', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating})"
    

class AssignmentSubmission(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to = 'submissions/')
    comment = models.TextField(blank = True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
