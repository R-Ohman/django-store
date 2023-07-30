from celery import shared_task

from email_app.models import EmailManager
from orders.models import Order, OrderItem
from products.models import Basket


@shared_task(bind=True)
def check_payment_status_task(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f'Order with ID {order_id} does not exist!'

    if order.status == Order.FORMING:
        order.status = Order.CANCEL
        order.save()
        order_items = OrderItem.objects.filter(order=order)
        for order_item in order_items:
            basket = Basket.objects.create(
                user=order.user,
                product=order_item.product,
                quantity=order_item.quantity
            )
        EmailManager.cancel_order(order)

        return 'Order {} has been cancelled!'.format(order.id)
    return 'Order {} has been paid!'.format(order.id)
