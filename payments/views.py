from urllib.parse import urlparse

from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from orders.models import Order
from payments.models import ExchangeRate
from products.models import Basket
from store.settings import LOGIN_URL, PAYPAL_RECEIVER_EMAIL

from paypal.standard.forms import PayPalPaymentsForm

from users.translator import translate_text_to_user_language
from payments.tasks import check_payment_status_task


@login_required(login_url=LOGIN_URL)
def make_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    amount = '%.2f' % order.sum
    currency_code = order.currency.code

    # UAH is not supported by PayPal (https://developer.paypal.com/api/rest/reference/currency-codes/)
    if order.currency.code == 'UAH':
        amount = '%.2f' % ExchangeRate.convert_to_base_currency(order.sum, order.currency)
        currency_code = 'USD'

    paypal_dict = {
        'business': PAYPAL_RECEIVER_EMAIL,
        'amount': amount,
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': currency_code,
        'notify_url': 'http://{}{}'.format(host, reverse('user:orders:paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('user:orders:payments:paypal-return')),
        'cancel_return': 'http://{}{}'.format(host, reverse('user:orders:payments:paypal-cancel')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)

    print(urlparse(request.META.get('HTTP_REFERER')).path)
    print(reverse('user:orders:orders_history'))

    if urlparse(request.META.get('HTTP_REFERER')).path == reverse('user:orders:orders_history'):
        messages.warning(request, translate_text_to_user_language(
                         'If you have already paid for your order, please wait for payment confirmation by email.\
                         In case of prolonged waiting please contact the site administration!', request))


    time_to_pay = 30 * 60       # 30 min
    check_payment_status_task.apply_async(args=[order_id], countdown=time_to_pay)

    context = {
        'form': form,
        'order': order,
    }

    return render(request, 'payments/payment.html', context)


def paypal_return(request):
    messages.success(request, translate_text_to_user_language('You have successfully made a payment!', request))
    return redirect('user:orders:orders_history')


def paypal_cancel(request):
    messages.error(request, translate_text_to_user_language('Payment has been cancelled!', request))
    order = Order.objects.get(id=request.POST['invoice'])
    order.status = Order.CANCEL
    order.save()
    order_items = Order.objects.filter(order=order)

    for order_item in order_items:
        basket = Basket.objects.create(
            user=request.user,
            product=order_item.product,
            quantity=order_item.quantity
        )

    return redirect('user:orders:orders_history')

