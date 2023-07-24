from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from orders.models import OrderItem
from users.translator import translate_text_to_user_language


def check_referer_no_keywords(request):
    referer = request.META.get('HTTP_REFERER')
    keywords = [
        reverse('user:registration'),
        reverse('user:reset_password'),
        reverse('user:logout'),
        reverse('user:login'),
    ]
    for keyword in keywords:
        if keyword in referer:
            return False
    return True


def user_received_product(request, product):
    if request.user.is_authenticated:
        user_order_items = OrderItem.objects.filter(order__user=request.user, product=product)
        for user_order_item in user_order_items:
            print(user_order_item.order.get_status_display())
            if user_order_item and user_order_item.order.get_status_display() == 'Completed':
                return True
    return request.user.is_staff


def refund_email(request, refund):
    user = request.user
    subject = translate_text_to_user_language('Confirmation of receipt of return request', request)
    message = render_to_string('users/email_refund_products.html', {
        'user': user,
        'refund': refund,
        'domain': get_current_site(request).domain,
    })

    email = EmailMultiAlternatives(subject, message, to=[user.email])
    email.attach_alternative(message, "text/html")

    if email.send():
        messages.success(request, translate_text_to_user_language(
            f'We have sent an confirmation of receipt of return request to your email ({user.email}). ', request))
    else:
        messages.error(request, translate_text_to_user_language(
            'Unfortunately, we were unable to send a confirmation of receipt of return request to your email.\
            However, you can find information about refunds in the "Orders" section or on your order page.', request))
