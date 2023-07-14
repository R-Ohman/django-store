from django.urls import path, include
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

from orders.views import place_order, orders_list, order_view
from payments.signals import valid_ipn_signal, invalid_ipn_signal

app_name = 'orders'

urlpatterns = [
    path('place/', place_order, name='place_order'),
    path('history/', orders_list, name='orders_history'),
    path('<int:pk>/', order_view, name='order_view'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment/', include('payments.urls', namespace='payments')),
]