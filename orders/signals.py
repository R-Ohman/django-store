from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from email_app.models import EmailManager
from orders.models import Order, OrderItem


@receiver(post_delete, sender=Order)
def update_product_quantity(sender, instance, **kwargs):
    order_items = instance.order_items.all()
    for order_item in order_items:
        product = order_item.product
        if product.quantity == 0 and order_item.quantity > 0:
            EmailManager.product_is_available(product)

        product.quantity += order_item.quantity
        product.save()


@receiver(post_delete, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    if product.quantity == 0 and instance.quantity > 0:
        EmailManager.product_is_available(product)

    product.quantity += instance.quantity
    product.save()


@receiver(pre_save, sender=OrderItem)
def update_product_quantity_on_order_item_save(sender, instance, **kwargs):
    print('update_product_quantity_on_order_item_save')
    if instance.pk:  # Check if the order item already exists
        try:
            original_order_item = OrderItem.objects.get(pk=instance.pk)
            quantity_diff = instance.quantity - original_order_item.quantity
            product = instance.product
            new_quantity = product.quantity - quantity_diff
            if new_quantity >= 0 and quantity_diff <= product.quantity:
                product.quantity = new_quantity
                product.save()
            else:
                raise ValueError("Invalid quantity change")
        except OrderItem.DoesNotExist:
            raise ValueError("OrderItem does not exist")
