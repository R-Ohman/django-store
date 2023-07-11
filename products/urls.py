from django.urls import path
from products.views import products
from products.views import add_product, delete_basket, basket_update, product_view

app_name = 'products'

urlpatterns = [
    path('', products, name='index'),
    path('<int:product_id>/', product_view, name='product_view'),
    path('category/<int:category_id>/', products, name='category'),
    path('category/<int:category_id>/page/<int:page>/', products, name='category_page'),
    path('basket/add/<int:product_id>/', add_product, name='basket_add'),
    path('basket/delete/<int:basket_id>/', delete_basket, name='basket_delete'),
    path('basket/update/<int:id>/', basket_update, name='basket_update'),
]