from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignUpTest(TestCase):
    '''Тестируем создание нового пользователя.'''

    def setUp(self):
        self.signup_url = reverse('users:signup')

    def test_signup_creates_new_user(self):
        '''Новый пользователь создается.'''
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

        response = self.client.post(self.signup_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        user = User.objects.get(username=data['username'])
        self.assertEqual(user.email, data['email'])
