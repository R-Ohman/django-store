from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED

from email_app.models import EmailManager
from orders.models import Order
from payments.models import ExchangeRate
from payments.utils import is_within_range, order_cancel_update_stock
from store.settings import PAYPAL_RECEIVER_EMAIL


def process_payment(sender, **kwargs):
    print('process_payment')
    ipn = sender
    if ipn.payment_status == ST_PP_COMPLETED:
        print('ST_PP_COMPLETED')
        order = Order.objects.get(id=ipn.invoice)

        order_sum = order.sum
        if order.currency.code == 'UAH':
            order_sum = ExchangeRate.convert_to_base_currency(order.sum, order.currency)

        if ipn.receiver_email != PAYPAL_RECEIVER_EMAIL or not is_within_range(ipn.mc_gross, order_sum, 0.1):
            # Not a valid payment
            print(f'Not a valid payment: {ipn.receiver_email} != {PAYPAL_RECEIVER_EMAIL} or {ipn.mc_gross} != {order.sum}')
            order_cancel_update_stock(order.id)
            return
        else:
            order.status = Order.PAID
        order.save()
        EmailManager.purchase_receipt(order)


@receiver(valid_ipn_received)
def valid_ipn_signal(sender, **kwargs):
    print('valid_ipn_signal')
    process_payment(sender, **kwargs)


@receiver(invalid_ipn_received)
def invalid_ipn_signal(sender, **kwargs):
    print('invalid_ipn_signal')
    process_payment(sender, **kwargs)
