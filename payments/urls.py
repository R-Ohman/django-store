from django.urls import path

from payments.views import make_payment, paypal_return, paypal_cancel

app_name = 'payments'

urlpatterns = [
    path('<int:order_id>/', make_payment, name='index'),
    path('return/', paypal_return, name='paypal-return'),
    path('cancel/', paypal_cancel, name='paypal-cancel'),
]
