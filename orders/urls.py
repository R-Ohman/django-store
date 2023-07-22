from django.urls import path, include
from orders.views import place_order, orders_list, order_view, cancel_order, request_refund


app_name = 'orders'

urlpatterns = [
    path('place/', place_order, name='place_order'),
    path('history/', orders_list, name='orders_history'),
    path('history/cancel/<int:pk>', cancel_order, name='cancel_order'),
    path('<int:pk>/', order_view, name='order_view'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment/', include('payments.urls', namespace='payments')),
    path('refund/<int:order_id>/', request_refund, name='request_refund'),
]