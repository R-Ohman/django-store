from django.db import models

#from users.models import User
#from payments.models import Currency

# Create your models here.
from payments.models import Currency
from store.settings import BASE_CURRENCY
from users.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class UserProductsQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(item.sum for item in self)

    def total_quantity(self):
        return sum(item.quantity for item in self)

    def currency(self):
        return self[0].currency if self else BASE_CURRENCY


class Product(models.Model):
    name = models.CharField(max_length=256, unique=True, blank=True)
    image = models.ImageField(upload_to='products_images', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)             # price in default currency (USD)
    quantity = models.PositiveIntegerField(default=0)                       # quantity in stock

    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name} | {self.name}'

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)

    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)      # price in currency

    add_datetime = models.DateTimeField(auto_now_add=True)
    objects = UserProductsQuerySet.as_manager()

    def __str__(self):
        return f'{self.user.username} | {self.product.name}'

    @property
    def sum(self):
        return self.quantity * self.price
