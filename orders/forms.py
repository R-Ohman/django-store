from django import forms
from django_countries.fields import CountryField

from orders.utils import validate_postal_code
from phonenumber_field.formfields import PhoneNumberField
from orders.models import Order, Refund
from users.translator import translate_text_to_user_language


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        self.request = request

        dict = {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email,
        }

        user_last_order = Order.objects.filter(user=self.request.user).last()
        if user_last_order:
            dict.update({
                'country': user_last_order.country,
                'address': user_last_order.address,
                'postal_code': user_last_order.postal_code,
                'phone': user_last_order.phone,
            })
            self.fields['country'].initial = user_last_order.country

        for field, label in dict.items():
            self.fields[field].widget.attrs['value'] = label

    def save(self, commit=True):
        order = super(OrderForm, self).save(commit=False)

        if self.request.user:
            order.user = self.request.user

        if commit:
            order.save()
        return order

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code']
        country_code = self.cleaned_data['country'].lower()
        if not validate_postal_code(country_code, postal_code):
            raise forms.ValidationError(
                translate_text_to_user_language("Invalid postal code format.", self.request))
        return postal_code


    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 2:
            raise forms.ValidationError(
                translate_text_to_user_language("Name should have at least 2 characters.", self.request))
        if len(first_name) > 100:
            raise forms.ValidationError(
                translate_text_to_user_language("Name should not exceed 100 characters.", self.request))
        if not first_name.isalpha():
            raise forms.ValidationError(
                translate_text_to_user_language("Name should only contain alphabetic characters.", self.request))
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 2:
            raise forms.ValidationError(
                translate_text_to_user_language("Last name should have at least 2 characters.", self.request))
        if len(last_name) > 100:
            raise forms.ValidationError(
                translate_text_to_user_language("Last name should not exceed 100 characters.", self.request))
        if not last_name.isalpha():
            raise forms.ValidationError(
                translate_text_to_user_language("Last name should only contain alphabetic characters.", self.request))
        return last_name

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'George',
    }), required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ohman',
    }), required=True)
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'aria-describedby': 'emailHelp',
        'placeholder': 'your_email@example.com',
    }), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ukraine, Kyiv, Khreschatyk street, 1',
    }), required=True)

    phone = PhoneNumberField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '+380 00 000 00 00',
    }), required=True)
    country = CountryField().formfield(widget=forms.Select(attrs={
        'class': 'form-control select-input',
    }), required=True)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '12345',
    }), required=True)

    class Meta:
        model = Order
        exclude = ['user', 'currency', 'status']


class RefundForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '4',
    }))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(RefundForm, self).__init__(*args, **kwargs)
        if request:
            self.fields['message'].widget.attrs['placeholder'] = translate_text_to_user_language('Enter extra information', request)

    class Meta:
        fields = ('message',)
        model = Refund
