from celery import shared_task

from email_app.models import EmailManager
from orders.models import Order, OrderItem
from payments.utils import order_cancel_update_stock
from products.models import Basket


@shared_task(bind=True)
def check_payment_status_task(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f'Order with ID {order_id} does not exist!'

    if order.status == Order.FORMING:
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            basket = Basket.objects.create(
                user=order.user,
                product=order_item.product,
                quantity=order_item.quantity
            )
        order_cancel_update_stock(order.id)
        EmailManager.cancel_order(order)
        return 'Order {} has been cancelled!'.format(order.id)
    else:
        return 'Order {} has been paid!'.format(order.id)
