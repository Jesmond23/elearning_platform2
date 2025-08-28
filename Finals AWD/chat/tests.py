from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import CustomUser
from chat.models import PrivateMessage

# Create your tests here.


class PrivateMessageApiTest(APITestCase):
    def setUp(self):
        self.sender = CustomUser.objects.create_user(username='sender', password='testpass')
        self.receiver = CustomUser.objects.create_user(username='receiver',password='testpass')
        self.url = reverse('send_private_message')

    def test_send_message_authenticated(self):
        self.client.login(username='sender',password='testpass')
        data = {
            'receiver': self.receiver.id,
            'content': 'Hello!',
            'room_name': 'room_1'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PrivateMessage.objects.count(),1)

    def test_send_message_unauthenticated(self):
        data = {
            'receiver': self.receiver.id,
            'content': 'Unauthorized',
            'room_name': 'room_1'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)