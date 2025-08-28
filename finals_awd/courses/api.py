from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from courses.models import Course, Enrollment
from accounts.models import CustomUser
from dashboard.serializers import UserSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_participant(request, course_id):
    course = get_object_or_404(Course, id = course_id)
    
    if request.user != course.teacher and not Enrollment.objects.filter(course=course,student= request.user).exists():
        return Response({"detail": "Not authorized for this course"}, status=403)

    participants = [enrollment.student for enrollment in course.enrollments.all()]

    data = {
        "teacher": UserSerializer(course.teacher).data,
        "students":UserSerializer(participants, many=True).data
    }

    return Response(data)