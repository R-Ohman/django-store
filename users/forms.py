from captcha.widgets import ReCaptchaV3
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from users.models import User
from users.translator import translate_text_to_user_language
from captcha.fields import ReCaptchaField


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserLoginForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['username'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your user name', request)

            self.fields['password'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your password', request)

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control py-4',
        'aria-describedby': 'emailHelp',
    }))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        if request:
            dict = {
                'first_name': translate_text_to_user_language('Enter your name', request),
                'last_name': translate_text_to_user_language('Enter your last name', request),
                'username': translate_text_to_user_language('Enter your user name', request),
                'password1': translate_text_to_user_language('Enter your password', request),
                'password2': translate_text_to_user_language('Enter your password', request),
                'email': translate_text_to_user_language('Enter your e-mail address', request),
            }
            for field, label in dict.items():
                self.fields[field].widget.attrs['placeholder'] = label

            self.fields['password1'].help_text = translate_text_to_user_language(
                'Your password must contain at least 8 characters, including both letters and numbers.', request)


    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'email',
            'first_name',
            'last_name'
        )


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'aria-describedby': 'usernameHelp',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control py-4',
        'aria-describedby': 'emailHelp',
    }))
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'custom-file-input',
    }), required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'image'
        )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if self.instance.is_confirmed:
            self.fields['email'].widget.attrs['disabled'] = True
            self.fields['email'].required = False
        else:
            self.fields['email'].help_text = translate_text_to_user_language('You will be required to confirm your email to access all site features. \
                                                            Viewing your email will be inaccessible to other users.', request)

        if not self.instance.number_of_available_username_changes:
            self.fields['username'].widget.attrs['disabled'] = True
            self.fields['username'].required = False
        else:
            self.fields['username'].help_text = translate_text_to_user_language('Username is used to log in to the account.\
                                                                                Note: You can change it once!', request)


    def clean_email(self):
        # If the email field is disabled, return the current value from the instance
        if self.fields['email'].widget.attrs.get('disabled') and self.fields['email'].widget.attrs['disabled']:
            return self.instance.email
        # Otherwise, return the cleaned value from the form data
        return self.cleaned_data['email']

    def clean_username(self):
        # If the username field is disabled, return the current value from the instance
        if self.fields['username'].widget.attrs.get('disabled') and self.fields['username'].widget.attrs['disabled']:
            return self.instance.username
        # Otherwise, return the cleaned value from the form data
        return self.cleaned_data['username']


class UserResetPasswordEmailForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-icon-trailing py-4',
        'aria-describedby': 'emailHelp',
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserResetPasswordEmailForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['email'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your e-mail address', request)

    class Meta:
        model = User
        fields = (
            'email',
        )


class UserResetPasswordForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserResetPasswordForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['password1'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter a new password', request)
            self.fields['password2'].widget.attrs['placeholder'] = translate_text_to_user_language('Confirm the new password', request)
            self.fields['password1'].help_text = translate_text_to_user_language(
                'Your password must contain at least 8 characters, including both letters and numbers.', request)

    class Meta:
        model = User
        fields = (
            'password1',
            'password2',
        )