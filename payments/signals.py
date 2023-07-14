from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from payments.utils import order_paid_update_stock


@receiver(valid_ipn_received)
def valid_ipn_signal(sender, **kwargs):
    print('invalid_ipn_signal')
    ipn = sender
    if ipn.payment_status == "Completed":
        order_paid_update_stock(sender)


@receiver(invalid_ipn_received)
def invalid_ipn_signal(sender, **kwargs):
    print('invalid_ipn_signal')
    ipn = sender
    if ipn.payment_status == "Completed":
        order_paid_update_stock(sender)
