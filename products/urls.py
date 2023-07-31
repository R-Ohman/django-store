from django.urls import path, include

from comments.views import product_view, image_view
from products.views import products
from . import views

app_name = 'products'

urlpatterns = [
    path('', products, name='index'),
    path('<int:product_id>/', product_view, name='view'),
    path('<int:product_id>/image/', image_view, name='image'),
    path('comments/', include('comments.urls', namespace='comments')),
    path('category/<int:category_id>/', products, name='category'),
    path('basket/add/<int:product_id>/', views.add_product, name='basket_add'),
    path('basket/delete/<int:basket_id>/', views.delete_basket, name='basket_delete'),
    path('basket/update/<int:id>/', views.basket_update, name='basket_update'),
    path('follow/<int:product_id>/', views.follow_product_availability, name='follow'),
    path('unfollow/<int:product_id>/', views.unfollow_product, name='unfollow'),
    path('discount_expiration/<int:product_id>/', views.product_discount_expiration, name='product_discount_expiration'),
]
