from django.urls import path, include
from users.views import login, registration, profile, logout, google_oauth2_login

app_name = 'user'

urlpatterns = [
    path('login/', login, name='login'),
    path('login/google', google_oauth2_login, name='google_oauth2_login'),
    path('registration/', registration, name='registration'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('orders/', include('orders.urls', namespace='orders')),
]