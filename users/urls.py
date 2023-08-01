from django.urls import path, include

from products.views import empty_cart
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('profile/empty-cart', empty_cart, name='empty_cart'),
    path('logout/', views.logout, name='logout'),
    path('orders/', include('orders.urls', namespace='orders')),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset/<uidb64>/<token>/', views.reset, name='reset'),
    path('reset/', views.reset_password, name='reset_password'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='wishlist_add'),
    path('wishlist/delete/<int:product_id>/', views.delete_from_wishlist, name='wishlist_delete'),
]