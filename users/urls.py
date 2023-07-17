from django.urls import path, include
from users.views import login, registration, profile, logout, activate

app_name = 'user'

urlpatterns = [
    path('login/', login, name='login'),
    path('registration/', registration, name='registration'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('orders/', include('orders.urls', namespace='orders')),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
]