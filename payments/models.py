from django.core.validators import MinValueValidator
from django.db import models
from store.settings import BASE_CURRENCY


class Currency(models.Model):

    code = models.CharField(max_length=3, unique=True)      # e.g. 'USD'
    name = models.CharField(max_length=100, unique=True)    # e.g. 'US Dollar'
    symbol = models.CharField(max_length=2, unique=True)    # e.g. '$'
    language = models.CharField(max_length=2, unique=True)  # e.g. 'en'

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'currency'
        verbose_name_plural = 'currencies'


class ExchangeRate(models.Model):
    base_currency = models.ForeignKey('payments.Currency', on_delete=models.CASCADE, blank=True,
                                      related_name='base_rates', default=None)
    target_currency = models.ForeignKey('payments.Currency', on_delete=models.CASCADE, related_name='target_rates')
    rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.base_currency} to {self.target_currency}: {self.rate}'

    @staticmethod
    def get_user_currency_and_converted_product_price(request, product):
        user_currency = Currency.objects.get(language=request.LANGUAGE_CODE)
        default_currency = Currency.objects.get(code=BASE_CURRENCY)

        exchange_rate = ExchangeRate.objects.filter(base_currency=default_currency,
                                                    target_currency=user_currency).first()
        converted_price = round( 2 * product.price * exchange_rate.rate) / 2
        return user_currency, converted_price

    @staticmethod
    def convert_to_base_currency(num, currency):
        default_currency = Currency.objects.get(code=BASE_CURRENCY)
        exchange_rate = ExchangeRate.objects.filter(base_currency=default_currency,
                                                    target_currency=currency).first()
        converted_price = round(2 * num / exchange_rate.rate) / 2
        return converted_price

    @staticmethod
    def convert_from_user_to_base(request, num):
        user_currency = Currency.objects.get(language=request.LANGUAGE_CODE)
        default_currency = Currency.objects.get(code=BASE_CURRENCY)
        exchange_rate = ExchangeRate.objects.filter(base_currency=default_currency,
                                                    target_currency=user_currency).first()
        converted_price = round(2 * num / exchange_rate.rate) / 2
        return converted_price

    @staticmethod
    def convert_to_user_currency(request, num):
        user_currency = Currency.objects.get(language=request.LANGUAGE_CODE)
        default_currency = Currency.objects.get(code=BASE_CURRENCY)
        exchange_rate = ExchangeRate.objects.filter(base_currency=default_currency,
                                                    target_currency=user_currency).first()
        converted_price = round(2 * num * exchange_rate.rate) / 2
        print(f'convert_to_user_currency {num} -> {converted_price}')
        return converted_price
