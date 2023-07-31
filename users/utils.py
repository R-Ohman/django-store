from django.urls import reverse
from orders.models import OrderItem, Order
import geoip2.database

def get_user_country(request):
    geoip_database = 'data/GeoLite2-Country.mmdb'
    user_ip = request.META.get('REMOTE_ADDR', None)
    if user_ip:
        reader = geoip2.database.Reader(geoip_database)

        try:
            response = reader.country(user_ip)
            country_code = response.country.iso_code
            return country_code
        except geoip2.errors.AddressNotFoundError:
            pass

    return 'en'


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
            if user_order_item and user_order_item.order.status == Order.COMPLETED:
                return True
    return request.user.is_staff
