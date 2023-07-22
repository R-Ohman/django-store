from deep_translator import GoogleTranslator
from django.urls import reverse
from orders.models import OrderItem


def translate_text_to_user_language(text, request):
    return GoogleTranslator(source='auto', target=request.LANGUAGE_CODE).translate(text)


def translate_text_to_language_by_currency(text, currency):
    return GoogleTranslator(source='auto', target=currency.language).translate(text)



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
            if user_order_item and user_order_item.order.get_status_display() == 'Finished':
                return True
    return request.user.is_staff
