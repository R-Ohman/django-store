from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED

from orders.models import Order
from payments.utils import order_paid_update_stock, is_within_range, receipt_email
from store.settings import PAYPAL_RECEIVER_EMAIL


def process_payment(sender, **kwargs):
    print('process_payment')
    ipn = sender
    if ipn.payment_status == ST_PP_COMPLETED:
        print('ST_PP_COMPLETED')
        order = Order.objects.get(id=ipn.invoice)

        if ipn.receiver_email != PAYPAL_RECEIVER_EMAIL or not is_within_range(ipn.mc_gross, order.sum, 0.1):
            # Not a valid payment
            print(f'Not a valid payment: {ipn.receiver_email} != {PAYPAL_RECEIVER_EMAIL} or {ipn.mc_gross} != {ipn.order.sum}')
            return

        order_paid_update_stock(sender)
        receipt_email(order)


@receiver(valid_ipn_received)
def valid_ipn_signal(sender, **kwargs):
    print('valid_ipn_signal')
    process_payment(sender, **kwargs)


@receiver(invalid_ipn_received)
def invalid_ipn_signal(sender, **kwargs):
    print('invalid_ipn_signal')
    process_payment(sender, **kwargs)
