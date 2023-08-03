from django import template
from decimal import Decimal
from payments.models import ExchangeRate
from products.utils import round_number

register = template.Library()

@register.filter
def converted_price(product, request):
    return round_number(ExchangeRate.convert_to_user_currency(request, product.price))

@register.filter
def converted_price_with_currency_symbol(product, request):
    user_currency, converted_price = ExchangeRate.get_user_currency_and_converted_product_price(request, product)
    return f'{round_number(converted_price)} {user_currency.symbol}'

@register.filter
def converted_discounted_price(product, request):
    return round_number(ExchangeRate.convert_to_user_currency(request, Decimal(str(product.discounted_price))))

@register.filter
def converted_discounted_price_with_currency_symbol(product, request):
    user_currency, converted_price = ExchangeRate.get_user_currency_and_converted_product_price(request, product)
    converted_price = converted_discounted_price(product, request)
    return f'{converted_price} {user_currency.symbol}'


@register.filter
def get_limited_description_length(product):
    if len(product.description) > 130:
        return product.description[:128] + '...'
    return product.description
