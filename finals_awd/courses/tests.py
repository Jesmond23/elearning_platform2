from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from dashboard.models import Notification, StatusUpdate
# Create your tests here.


#Test Teacher upload material with notification to students
from django.core.files.uploadedfile import SimpleUploadedFile
from courses.models import CourseMaterial

#Test User API
# from rest_framework import APIClient

    
User = get_user_model()

class EnrollmentTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher1',password='pass',is_teacher = True)
        self.student = User.objects.create_user(username='student1', password='pass', is_student = True)
        self.course = Course.objects.create(title='Test Course',teacher = self.teacher)

    def test_student_enrolled_and_teacher_notified(self):
        self.client.login(username='student1',password='pass')
        response = self.client.get(reverse('enroll_course', args=[self.course.id]))

        self.assertEqual(response.status_code,302)
        self.assertTrue(Enrollment.objects.filter(course=self.course, student=self.student).exists())
        self.assertTrue(Notification.objects.filter(
            recipient=self.teacher,
            course=self.course,
            notification_type = 'enrolment'
        ).exists())


class MaterialUploadTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher1', password='pass', is_teacher=True)
        self.student = User.objects.create_user(username='student1', password='pass', is_student=True)
        self.course = Course.objects.create(title='Upload Course', teacher=self.teacher)
        Enrollment.objects.create(course=self.course, student=self.student)

    def test_teacher_upload_material_and_student_notified(self):
        self.client.login(username='teacher1',password='pass')
        with open('testfile.pdf', 'wb') as f: f.write(b'%PDF-1.4 test file')

        with open('testfile.pdf', 'rb') as f:
            response = self.client.post(reverse('upload_material', args=[self.course.id]),{
                'title': 'Lecture 1',
                'file' : SimpleUploadedFile('testfile.pdf', f.read(), content_type='application/pdf')


            })
            
        self.assertEqual(response.status_code,302)
        self.assertTrue(CourseMaterial.objects.filter(course=self.course, title='Lecture 1').exists())
        self.assertTrue(Notification.objects.filter(
            recipient=self.student,
            course=self.course,
            notification_type = 'material_upload'
        ).exists())


class StatusUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='pass', is_student=True)


    def test_post_status_update(self):
        self.client.login(username='student1', password='pass')
        response = self.client.post(reverse('dashboard'),{
            'status_submit': '1',
            'content': 'This is a test post'
        })

        self.assertEqual(response.status_code,302)
        self.assertTrue(StatusUpdate.objects.filter(user=self.user, content='This is a test post').exists())


class CourseParticipantsApiTest(APITestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(username='teacher', password='pass', is_teacher=True)
        self.student = CustomUser.objects.create_user(username='student', password='pass', is_student=True)
        self.course = Course.objects.create(title='Test Course', teacher=self.teacher)
        Enrollment.objects.create(course=self.course, student=self.student)

    def test_teacher_can_access_participants(self):
        self.client.login(username='teacher', password='pass')
        url = reverse('course_participants', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('students', response.data)

    def test_student_can_access_participants(self):
        self.client.login(username='student', password='pass')
        url = reverse('course_participants', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_cannot_access(self):
        other_user = CustomUser.objects.create_user(username='outsider', password='pass')
        self.client.login(username='outsider', password='pass')
        url = reverse('course_participants', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)