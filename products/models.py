from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from users.models import User, Order


# Create your models here.

class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class BasketQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(basket.sum() for basket in self)

    def total_quantity(self):
        return sum(basket.quantity for basket in self)


class Product(models.Model):
    name = models.CharField(max_length=256, unique=True, blank=True)
    image = models.ImageField(upload_to='products_images', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name} | {self.name}'

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    add_datetime = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()
    def __str__(self):
        return f'{self.user.username} | {self.product.name}'

    def sum(self):
        return self.quantity * self.product.price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = BasketQuerySet.as_manager()
    def __str__(self):
        return f'{self.id} | {self.product.name}'

    class Meta:
        verbose_name = 'order item'
        verbose_name_plural = 'order items'

    def sum(self):
        return self.quantity * self.product.price

@receiver(post_delete, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    product.quantity += instance.quantity
    product.save()
