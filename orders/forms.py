from django import forms

from orders.models import Order


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        self.user = user

        user_last_order = Order.objects.filter(user=self.user).last()

        dict = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'address': user_last_order.address if user_last_order else '',
        }
        for field, label in dict.items():
            self.fields[field].widget.attrs['value'] = label

    def save(self, commit=True):
        order = super(OrderForm, self).save(commit=False)
        # Now you can access self.user and associate it with the order
        if self.user:
            order.user = self.user

        if commit:
            order.save()
        return order

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

    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
        )
