from django.urls import path, include

from products.views import empty_cart
from users.views import login, registration, profile, logout, activate, reset_password, reset

app_name = 'user'

urlpatterns = [
    path('login/', login, name='login'),
    path('registration/', registration, name='registration'),
    path('profile/', profile, name='profile'),
    path('profile/empty-cart', empty_cart, name='empty_cart'),
    path('logout/', logout, name='logout'),
    path('orders/', include('orders.urls', namespace='orders')),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('reset/<uidb64>/<token>/', reset, name='reset'),
    path('reset/', reset_password, name='reset_password'),
]