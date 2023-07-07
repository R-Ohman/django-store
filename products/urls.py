from django.urls import path
from products.views import products
from products.views import add_product, delete_busket, basket_update

app_name = 'products'

urlpatterns = [
    path('', products, name='index'),
    path('category/<int:category_id>/', products, name='category'),
    path('category/<int:category_id>/page/<int:page>/', products, name='category_page'),
    path('basket/add/<int:product_id>/', add_product, name='basket_add'),
    path('basket/delete/<int:id>/', delete_busket, name='basket_delete'),
    path('basket/update/<int:id>/', basket_update, name='basket_update'),
]