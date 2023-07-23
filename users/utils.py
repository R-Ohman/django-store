from django.urls import reverse
from orders.models import OrderItem


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
