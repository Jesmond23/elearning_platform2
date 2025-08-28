from rest_framework import serializers
from accounts.models import CustomUser
from courses.models import Course
from dashboard.models import Notification


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model= Course
        fields=['id','title','description']


class UserSerializer(serializers.ModelSerializer):
    enrolled_courses = serializers.SerializerMethodField()
    teaching_courses = CourseSerializer(source='courses_taught', many=True)


    class Meta:
        model = CustomUser
        fields=['id','username','email','is_student',
                'is_teacher','profile_picture','enrolled_courses','teaching_courses']
        
    def get_enrolled_courses(self, obj):
        if obj.is_student:
        # Get all courses the student is enrolled in via enrollment
            return CourseSerializer([en.course for en in obj.enrollments.all()], many=True).data
        return []
        
    def get_teaching_courses(self, obj):
        if obj.is_teacher:
            return CourseSerializer(obj.teaching_courses.all(), many=True).data
        return []
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'message', 'course', 'notification_type', 'is_read', 'created_at']