from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory

from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserResetPasswordEmailForm, UserResetPasswordForm
from users.models import User
from unittest.mock import patch
from users.translator import translate_text_to_user_language
from captcha.client import RecaptchaResponse
from PIL import Image
import io


class UserLoginFormTest(TestCase):

    def test_fields_attributes(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.LANGUAGE_CODE = 'en'

        form = UserLoginForm(request=request)

        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control py-4')
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-control py-4')

        expected_username_placeholder = 'Enter your user name'
        expected_password_placeholder = 'Enter your password'
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], expected_username_placeholder)
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], expected_password_placeholder)

    def test_translated_fields_attributes(self):
        request_factory = RequestFactory()
        request = request_factory.get('/')
        request.LANGUAGE_CODE = 'pl'

        form = UserLoginForm(request=request)

        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control py-4')
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-control py-4')

        expected_username_placeholder = translate_text_to_user_language('Enter your user name', request)
        expected_password_placeholder = translate_text_to_user_language('Enter your password', request)

        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], expected_username_placeholder)
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], expected_password_placeholder)

    def test_form_meta(self):
        form = UserLoginForm()
        self.assertEqual(form.Meta.model.__name__, 'User')
        self.assertEqual(form.Meta.fields, ('username', 'password'))

    def test_form_captcha(self):
        form = UserLoginForm()
        self.assertEqual(form.fields['captcha'].widget.__class__.__name__, 'ReCaptchaV3')

    @patch('captcha.fields.ReCaptchaField.clean')  # mock clean method from captcha.fields.ReCaptchaField
    def test_login_form_is_not_valid(self, mock_clean):
        mock_clean.return_value = True

        form = UserLoginForm(data={
            'username': 'test',
            'password': 'test',
        })
        self.assertFalse(form.is_valid())

        form = UserLoginForm(data={
            'username': '',
            'password': 'test',
        })
        self.assertFalse(form.is_valid())

        form = UserLoginForm(data={
            'username': 'test',
            'password': '',
        })
        self.assertFalse(form.is_valid())

        form = UserLoginForm(data={})
        self.assertFalse(form.is_valid())

    @patch('captcha.fields.ReCaptchaField.clean')  # mock clean method from captcha.fields.ReCaptchaField
    def test_login_form_is_valid(self, mock_clean):
        User.objects.create_user(username='test', password='password')
        mock_clean.return_value = True

        form = UserLoginForm(data={
            'username': 'test',
            'password': 'password',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.non_field_errors(), [])

    def test_login_wrong_captha(self):
        User.objects.create_user(username='test', password='password')

        form = UserLoginForm(data={
            'username': 'test',
            'password': 'password',
        })
        self.assertFalse(form.is_valid())

    @patch('captcha.fields.ReCaptchaField.clean')  # mock clean method from captcha.fields.ReCaptchaField
    def test_login_wrong_password(self, mock_clean):
        User.objects.create_user(username='test', password='password')
        mock_clean.return_value = True

        form = UserLoginForm(data={
            'username': 'test',
            'password': 'wrong_password',
        })
        self.assertFalse(form.is_valid())

        self.assertEqual(form.non_field_errors(), \
                         ['Please enter a correct username and password. Note that both fields may be case-sensitive.'])


class UserRegistrationFormTest(TestCase):

    def test_fields_attributes(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request)

        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control py-4')
        self.assertEqual(form.fields['email'].widget.attrs['class'], 'form-control py-4')
        self.assertEqual(form.fields['password1'].widget.attrs['class'], 'form-control py-4')
        self.assertEqual(form.fields['password2'].widget.attrs['class'], 'form-control py-4')

        expected_username_placeholder = 'Enter your user name'
        expected_email_placeholder = 'Enter your e-mail address'
        expected_password1_placeholder = 'Enter your password'
        expected_password2_placeholder = 'Repeat your password'
        expected_first_name_placeholder = 'Enter your name'
        expected_last_name_placeholder = 'Enter your last name'
        expected_help_text = 'Your password must contain at least 8 characters, including both letters and numbers.'

        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], expected_username_placeholder)
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], expected_email_placeholder)
        self.assertEqual(form.fields['password1'].widget.attrs['placeholder'], expected_password1_placeholder)
        self.assertEqual(form.fields['password2'].widget.attrs['placeholder'], expected_password2_placeholder)
        self.assertEqual(form.fields['first_name'].widget.attrs['placeholder'], expected_first_name_placeholder)
        self.assertEqual(form.fields['last_name'].widget.attrs['placeholder'], expected_last_name_placeholder)
        self.assertEqual(form.fields['password1'].help_text, expected_help_text)

    def test_translated_fields_attributes(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'pl'
        form = UserRegistrationForm(request=request)

        expected_username_placeholder = translate_text_to_user_language('Enter your user name', request)
        expected_email_placeholder = translate_text_to_user_language('Enter your e-mail address', request)
        expected_password1_placeholder = translate_text_to_user_language('Enter your password', request)
        expected_password2_placeholder = translate_text_to_user_language('Repeat your password', request)
        expected_first_name_placeholder = translate_text_to_user_language('Enter your name', request)
        expected_last_name_placeholder = translate_text_to_user_language('Enter your last name', request)
        expected_help_text = translate_text_to_user_language('Your password must contain at least 8 characters, including both letters and numbers.', request)

        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], expected_username_placeholder)
        self.assertEqual(form.fields['email'].widget.attrs['placeholder'], expected_email_placeholder)
        self.assertEqual(form.fields['password1'].widget.attrs['placeholder'], expected_password1_placeholder)
        self.assertEqual(form.fields['password2'].widget.attrs['placeholder'], expected_password2_placeholder)
        self.assertEqual(form.fields['first_name'].widget.attrs['placeholder'], expected_first_name_placeholder)
        self.assertEqual(form.fields['last_name'].widget.attrs['placeholder'], expected_last_name_placeholder)
        self.assertEqual(form.fields['password1'].help_text, expected_help_text)

    def test_form_meta(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request)

        self.assertEqual(form.Meta.model.__name__, 'User')
        self.assertEqual(form.Meta.fields, ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'))

    def test_registration_form_is_valid(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': 'test',
            'email': 'test@email.com',
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertTrue(form.is_valid())

    def test_registration_form_is_empty(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={})
        self.assertFalse(form.is_valid())
        self.assertRaises(ValueError, form.save)

        form = UserRegistrationForm(request=request, data={
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'first_name': '',
            'last_name': '',
        })
        self.assertFalse(form.is_valid())
        self.assertRaises(ValueError, form.save)

    def test_registration_repeat_password(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': 'test',
            'email': 'test@email.com',
            'password1': 'test_password1',
            'password2': 'test_password2',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['The two password fields didn’t match.'])

    def test_wrong_fields(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': '1234',
            'email': 'test@email',
            'password1': '1234',
            'password2': '1234',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertFalse(form.is_valid())

        self.assertIn('The password is too similar to the username.', form.errors['password2'])
        self.assertIn('This password is too short. It must contain at least 8 characters.', form.errors['password2'])
        self.assertIn('This password is too common.', form.errors['password2'])
        self.assertIn('This password is entirely numeric.', form.errors['password2'])
        self.assertIn('Enter a valid email address.', form.errors['email'])

    def test_registration_form_save(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': 'test',
            'email': 'test@email.com',
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, form.cleaned_data['email'])
        self.assertEqual(user.first_name, form.cleaned_data['first_name'])
        self.assertEqual(user.last_name, form.cleaned_data['last_name'])
        self.assertTrue(user.check_password(form.cleaned_data['password1']))

    def test_registration_existing_user(self):
        User.objects.create_user(
            username='test',
            email='test@email.com',
            password='test_password'
        )

        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': 'test',
            'email': 'test@email.com',
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('User with this Username already exists.', form.errors['username'])
        self.assertIn('User with this Email already exists.', form.errors['email'])

    def test_registration_form_save_user(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserRegistrationForm(request=request, data={
            'username': 'test',
            'email': 'test@email.com',
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_confirmed)
        self.assertEqual(user.number_of_available_username_changes, 1)
        user.save()


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test_password',
            email='test@email.com',
            first_name='test_name',
            last_name='test_last_name',
        )

    def test_form_fields(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserProfileForm(instance=self.user, request=request)

        self.assertEqual(form.instance, self.user)

        self.assertFalse(self.user.is_confirmed)
        self.assertEqual(form.fields['email'].help_text,
                         'You will be required to confirm your email to access all site features. Viewing your email will be inaccessible to other users.')

        self.assertEqual(self.user.number_of_available_username_changes, 1)
        self.assertEqual(form.fields['username'].help_text,
                         'Username is used to log in to the account. Note: You can change it once!')


        self.user.is_confirmed = True
        self.user.number_of_available_username_changes = 0
        form = UserProfileForm(instance=self.user, request=request)

        self.assertEqual(form.fields['email'].help_text, '')
        self.assertTrue(form.fields['email'].widget.attrs['disabled'])
        self.assertFalse(form.fields['email'].required)

        self.assertEqual(form.fields['username'].help_text, '')
        self.assertFalse(form.fields['username'].required)
        self.assertTrue(form.fields['username'].widget.attrs['disabled'])

    def test_form_save(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserProfileForm(instance=self.user, request=request, data={
            'username': 'test2',
            'email': 'test2@email.com',
            'first_name': 'test_name2',
            'last_name': 'test_last_name2',
        })

        self.assertTrue(form.is_valid())
        self.user = form.save()
        self.assertEqual(self.user.username, 'test2')
        self.assertEqual(self.user.email, form.cleaned_data['email'])
        self.assertEqual(self.user.first_name, form.cleaned_data['first_name'])
        self.assertEqual(self.user.last_name, 'test_last_name2')

    def test_form_save_existing_user(self):
        User.objects.create_user(
            username='test2',
            password='test_password',
            email='test2@email.com'
        )
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserProfileForm(instance=self.user, request=request, data={
            'username': 'test2',
            'email': 'test2@email.com',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('User with this Username already exists.', form.errors['username'])
        self.assertIn('User with this Email already exists.', form.errors['email'])

    def test_form_save_the_same_data(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'
        form = UserProfileForm(instance=self.user, request=request, data={
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        })
        self.assertTrue(form.is_valid())
        self.user = form.save()

    def test_upload_image(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'

        fake_image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        fake_image.save(image_io, format='PNG')

        form = UserProfileForm(instance=self.user, request=request, data={
            'username': 'test2',
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }, files={
            'image': SimpleUploadedFile('test_image.jpg', image_io.getvalue())
        })
        self.assertTrue(form.is_valid())
        self.user = form.save()
        self.assertTrue(self.user.image)
        self.assertTrue('users_images/test_image' in self.user.image.name)

    def test_upload_wrong_image(self):
        request = RequestFactory().get('/')
        request.LANGUAGE_CODE = 'en'

        fake_file_content = b'This is not an image file.'
        fake_file_io = io.BytesIO(fake_file_content)

        form = UserProfileForm(instance=self.user, request=request, data={
            'username': 'test2',
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }, files={
            'image': SimpleUploadedFile('test_image.jpg', fake_file_io.getvalue())
        })
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertIn('Upload a valid image. The file you uploaded was either not an image or a corrupted image.',
                        form.errors['image'])
