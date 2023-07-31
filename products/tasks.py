from celery import shared_task
from django.utils import timezone

from email_app.models import EmailManager
from orders.models import Order
from payments.utils import order_cancel_update_stock
from products.models import Product


@shared_task
def check_products_availability():
    unavailable_products = Product.objects.filter(visible=True, quantity=0)
    EmailManager.unavailable_products_notification(unavailable_products)
    return 'Unavailable products checked.'


@shared_task
def check_expired_discounts():
    products = Product.objects.all(visible=True)
    for product in products:
        if product.discount_end_date and product.discount_end_date >= timezone.now():
            product.discount_percentage = None
            product.discount_end_date = None
        product.save()
    return 'Discounts checked.'


@shared_task
def check_overdue_payments():
    orders = Order.objects.filter(status=Order.FORMING)
    for order in orders:
        delta = timezone.now() - order.created_at
        time_to_pay = 1800      # 30 minutes
        if delta.seconds > time_to_pay:
            order_cancel_update_stock(order.id)
    return 'Overdue payments checked.'