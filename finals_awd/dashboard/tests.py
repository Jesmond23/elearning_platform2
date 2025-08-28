from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import CustomUser

class CurrentUserApiTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='tester', password='password123')

    def test_user_api_authenticated(self):
        self.client.login(username='tester', password='password123')
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['username'], 'tester')

    def test_user_api_unauthenticated(self):
        response = self.client.get(reverse('user_api'))
        self.assertEqual(response.status_code, 403)
