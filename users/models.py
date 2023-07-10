from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver

import products
from store.translator import translate_text_to_user_language


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True)

class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'

    STATUSES = (
        (FORMING, 'Forming'),
        (SENT_TO_PROCEED, 'Sent to proceed'),
        (PROCEEDED, 'Proceeded'),
        (PAID, 'Paid'),
        (READY, 'Ready'),
        (CANCEL, 'Canceled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True, db_index=True)

    email = models.EmailField(max_length=128)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, choices=STATUSES, default=FORMING)

    def __str__(self):
        return f'{self.id} | {self.user.username}'

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'

    def sum(self):
        order_items = products.models.OrderItem.objects.filter(order=self)
        total_sum = sum(item.sum() for item in order_items)
        return total_sum

@receiver(post_delete, sender=Order)
def update_product_quantity(sender, instance, **kwargs):
    order_items = instance.orderitem_set.all()
    for order_item in order_items:
        product = order_item.product
        product.quantity += order_item.quantity
        product.save()