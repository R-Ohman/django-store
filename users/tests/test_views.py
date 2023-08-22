from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from users.models import User


class LoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser',
                            password='testpassword')

    def test_login_view_get(self):
        response = self.client.get(reverse('user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_already_logged_in(self):
        user = User.objects.get(username='testuser')
        self.client.force_login(user)

        response = self.client.post(reverse('user:login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:profile'))


    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('user:login'), {'username': 'testuser',
                                                            'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
