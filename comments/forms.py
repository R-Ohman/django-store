from captcha.widgets import ReCaptchaV3
from django import forms

from comments.models import ProductComment, UserReport
from users.translator import translate_text_to_user_language
from captcha.fields import ReCaptchaField

class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '4',
    }))
    assessment = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'min': '2',
        'max': '5',
        'step': '0.5',
    }))

    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['text'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your comment', request)
            self.fields['assessment'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your assessment', request)

    class Meta:
        fields = ('text', 'assessment')
        model = ProductComment


class UserReportForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
    }))
    topic = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '4',
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(UserReportForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['text'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter your report', request)

    class Meta:
        fields = ('name', 'email', 'topic', 'text')
        model = UserReport
