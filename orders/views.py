from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from orders.forms import OrderForm, RefundForm
from orders.models import OrderItem, Order, Refund, RefundAttachment, RefundProduct
from products.models import Basket
from store.settings import LOGIN_URL
from payments.models import Currency
from users.translator import translate_text_to_user_language
from users.utils import refund_email


@login_required(login_url=LOGIN_URL)
def place_order(request):
    if not request.user.is_confirmed:
        messages.error(request, translate_text_to_user_language('Please confirm your email address to place an order.', request))
        return HttpResponseRedirect(reverse('user:profile'))

    baskets = Basket.objects.filter(user=request.user)
    form = OrderForm(request=request)
    errors = []

    if request.method == 'POST' and request.POST['currency_id']:
        form = OrderForm(data=request.POST, request=request)
        if form.is_valid():
            for basket in baskets:
                if basket.product.quantity < basket.quantity:
                    errors.append(translate_text_to_user_language('There are not enough items in stock.', request))
                    break

            if not baskets or not form.is_valid():
                errors.append(translate_text_to_user_language('Error during order execution.', request))
            else:
                order = form.save(commit=False)
                order.user = request.user
                order.currency = Currency.objects.get(id=int(request.POST['currency_id']))

                order.save()

                for basket in baskets:
                    #currency, price = ExchangeRate.get_user_currency_and_converted_product_price(request, basket.product)
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=basket.product,
                        quantity=basket.quantity,
                        price=basket.discounted_price,
                    )

                baskets.delete()

                return HttpResponseRedirect(reverse('user:orders:payments:index', args=(order.id,)))


    context = {
        'baskets': baskets,
        'total_sum': baskets.total_sum(),
        'total_quantity': baskets.total_quantity(),
        'errors': errors,
        'form': form,
    }

    for field, error in form.errors.items():
        context['errors'].append(error)
        print(field, " - " ,error)

    return render(request, 'orders/order-create.html', context)


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    current_orders = []
    past_orders = []
    for order in orders:
        if order.status in [Order.CANCEL, Order.COMPLETED]:
            past_orders.append(order)
        else:
            current_orders.append(order)

    refunds = Refund.objects.filter(order__in=orders).order_by('-id')

    context = {
        'current_orders': current_orders,
        'past_orders': past_orders,
        'refunds': refunds,
    }

    return render(request, 'orders/orders.html', context)


@login_required
def order_view(request, pk):
    order = Order.objects.get(id=pk)

    context = {
        'order': order,
        'product_baskets': OrderItem.objects.filter(order=order),
        'maps': 'https://www.google.com/maps/search/' + order.address.replace(' ', '+'),
    }
    return render(request, 'orders/order-view.html', context)


@login_required
def cancel_order(request, pk):
    order = Order.objects.get(id=pk)
    order.status = Order.CANCEL
    order.save()
    return HttpResponseRedirect(reverse('user:orders:orders_history'))


@login_required
def request_refund(request, order_id):
    order = Order.objects.get(id=order_id)
    if not order.can_refund:
        messages.error(request, translate_text_to_user_language('You can not request a refund!', request))
        return redirect(request.META.get('HTTP_REFERER', reverse('user:orders:orders_history')))

    if request.method == 'POST':
        form = RefundForm(request.POST, request=request)
        files = request.FILES.getlist('files')

        refund_items = request.POST.getlist('refund-item')
        refund_quantities = request.POST.getlist('refund-item-quantity')
        reasons = request.POST.getlist('refund-item-reason')
        if form.is_valid():
            message = form.cleaned_data['message']
            refund = Refund.objects.create(
                message=message,
                order=order,
            )

            for file in files:
                RefundAttachment.objects.create(
                    refund=refund,
                    file=file
                )

            for item_id, quantity, reason in zip(refund_items, refund_quantities, reasons):
                ordered_product = get_object_or_404(OrderItem, id=item_id)
                quantity = int(quantity)

                if 0 < quantity <= ordered_product.quantity:
                    RefundProduct.objects.create(
                        refund=refund,
                        ordered_product=ordered_product,
                        quantity=quantity,
                        reason=reason,
                    )
                else:
                    refund.delete()
                    messages.error(request, translate_text_to_user_language('Invalid quantity!', request))
                    return redirect(request.META.get('HTTP_REFERER', reverse('user:orders:orders_history')))

            if refund:
                refund_email(request, refund)

            return redirect(reverse('user:orders:order_view', args=(order.id,)))
        else:
            print("errors: ", form.errors)
    else:
        form = RefundForm(request=request)

    context = {
        'form': form,
        'order_items': OrderItem.objects.filter(order=order),
        'order': order,
        'reasons': [reason[1] for reason in Refund.get_reason_choices(request)],
    }

    return render(request, 'orders/refund.html', context)
