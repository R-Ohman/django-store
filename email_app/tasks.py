from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from orders.models import Order, OrderItem, Refund
from products.models import Product
from store.settings import SITE_DOMAIN
from users.models import User
from users.translator import translate_text_to_language_by_currency, translate_text_to_language
from users.tokens import account_activation_token


@shared_task
def email_reset_password_task(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f'User with ID {user_id} does not exist!'

    subject = translate_text_to_language('Reset password', user.country_code)
    message = render_to_string('email_app/reset_password.html', {
        'user': user,
        'domain': SITE_DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    if user.email_user(subject, message):
        return f'reset_password sent (user_id={user_id})'
    else:
        return f'reset_password not sent (user_id={user_id})'


@shared_task
def email_activate_account_task(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f'User with ID {user_id} does not exist!'

    mail_subject = translate_text_to_language('Activate your account.', user.country_code)
    message = render_to_string('email_app/activate_account.html', {
        'user': user.username,
        'domain': SITE_DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    if email.send():
        return f'activation_email sent (user_id={user_id})'
    else:
        return f'activation_email not sent (user_id={user_id})'


@shared_task
def email_refund_requested_task(refund_id):
    try:
        refund = Refund.objects.get(id=refund_id)
    except Refund.DoesNotExist:
        return f'Refund with ID {refund_id} does not exist!'

    user = refund.order.user
    subject = translate_text_to_language('Confirmation of receipt of return request', user.country_code)
    message = render_to_string('email_app/refund_products.html', {
        'user': user,
        'refund': refund,
        'domain': SITE_DOMAIN,
    })

    email = EmailMultiAlternatives(subject, message, to=[user.email])
    email.attach_alternative(message, "text/html")

    if email.send():
        return f'refund_email sent (refund_id={refund_id})'
    else:
        return f'refund_email not sent (refund_id={refund_id})'


@shared_task
def email_purchase_receipt_task(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f'Order with ID {order_id} does not exist!'

    subject = "Store | " + translate_text_to_language_by_currency(f'Purchase receipt №{order.id}', order.currency)

    message = render_to_string('email_app/purchase_receipt.html', {
        'order': order,
        'order_items': OrderItem.objects.filter(order=order),
        'domain': SITE_DOMAIN,
    })

    email = EmailMultiAlternatives(subject, message, to=[order.email])
    email.attach_alternative(message, "text/html")

    if email.send():
        return f'receipt_email sent (order_id={order_id})'
    else:
        return f'receipt_email not sent (order_id={order_id})'


@shared_task
def email_invite_and_recommendation_task(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f'User with ID {user_id} does not exist!'

    subject = translate_text_to_language(f'Hi, {user.first_name}, we have a special offer for you!',
                                         user.country_code)

    discount_products = Product.objects.filter(discount_percentage__gt=0).order_by('-discount_percentage')[:3]

    message = render_to_string('email_app/invite_and_recommendations.html', {
        'products': discount_products,
        'domain': SITE_DOMAIN,
    })

    email = EmailMultiAlternatives(subject, message, to=[user.email])
    email.attach_alternative(message, "text/html")
    if email.send():
        return f'invite_and_recommendation sent (user_id={user_id})'
    else:
        return f'invite_and_recommendation not sent (user_id={user_id})'


@shared_task
def email_cancel_order_task(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f'Order with ID {order_id} does not exist!'

    subject = translate_text_to_language_by_currency(f'Order №{order.id} has been cancelled', order.currency)

    message = render_to_string('email_app/cancel_order.html', {
        'order': order,
        'order_items': OrderItem.objects.filter(order=order),
        'domain': SITE_DOMAIN,
    })

    email = EmailMultiAlternatives(subject, message, to=[order.email])
    email.attach_alternative(message, "text/html")

    if email.send():
        return f'cancel_order sent (order_id={order_id})'
    else:
        return f'cancel_order not sent (order_id={order_id})'
