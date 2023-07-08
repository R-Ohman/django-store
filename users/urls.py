from django.urls import path
from users.views import login, registration, profile, logout, place_order, orders_list, order_view

app_name = 'user'

urlpatterns = [
    path('login/', login, name='login'),
    path('registration/', registration, name='registration'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('place_order/', place_order, name='place_order'),
    path('orders_history/', orders_list, name='orders_history'),
    path('order/<int:pk>/', order_view, name='order_view'),
]