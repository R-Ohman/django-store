from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser',
                            email='testemail@gmail.com',
                            password='testpassword')

    def test_user_creation(self):
        user = User.objects.get(id=1)
        expected_username = user.username
        expected_email = user.email
        expected_password = user.password
        self.assertEqual(expected_username, 'testuser')
        self.assertEqual(expected_email, 'testemail@gmail.com')
        self.assertEqual(expected_password, 'testpassword')
        self.assertFalse(user.is_confirmed)
        self.assertEqual(user.number_of_available_username_changes, 1)
        self.assertEqual(user.country_code, 'en')
        self.assertEqual(str(user), 'testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_update(self):
        user = User.objects.get(id=1)
        user.username = 'newusername'
        user.email = 'new_email'

        self.assertEqual(user.username, 'newusername')
        self.assertEqual(user.email, 'new_email')

    def test_user_delete(self):
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(id=1)
        user.delete()
        self.assertEqual(User.objects.count(), 0)

