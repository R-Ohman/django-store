from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from users.models import User
from users.utils import translate_text_to_user_language


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control py-4',
    }))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserLoginForm, self).__init__(*args, **kwargs)
        if request:
            dict = {
                'username': translate_text_to_user_language('Enter your user name', request),
                'password': translate_text_to_user_language('Enter your password', request),
            }
            for field, label in dict.items():
                self.fields[field].widget.attrs['placeholder'] = label


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
    }), disabled=True)
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control py-4',
        'aria-describedby': 'emailHelp',
    }), disabled=True)
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
