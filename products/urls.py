from django.urls import path, include
from products.views import products
from products.views import add_product, delete_basket, basket_update, product_discount_expiration

app_name = 'products'

urlpatterns = [
    path('', products, name='index'),
    path('comments/', include('comments.urls', namespace='comments')),
    path('category/<int:category_id>/', products, name='category'),
    path('basket/add/<int:product_id>/', add_product, name='basket_add'),
    path('basket/delete/<int:basket_id>/', delete_basket, name='basket_delete'),
    path('basket/update/<int:id>/', basket_update, name='basket_update'),
    path('discount_expiration/<int:product_id>/', product_discount_expiration, name='product_discount_expiration'),
]
