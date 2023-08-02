from decimal import Decimal
from django.test import TestCase, RequestFactory

from payments.models import Currency, ExchangeRate
from products.models import Product, ProductCategory
from users.models import User


class CurrencyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')

    def test_code_label(self):
        currency = Currency.objects.get(id=1)
        field_label = currency._meta.get_field('code').verbose_name
        self.assertEquals(field_label, 'code')

    def test_code_max_length(self):
        currency = Currency.objects.get(id=1)
        max_length = currency._meta.get_field('code').max_length
        self.assertEquals(max_length, 3)

    def test_name_label(self):
        currency = Currency.objects.get(id=1)
        field_label = currency._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_name_max_length(self):
        currency = Currency.objects.get(id=1)
        max_length = currency._meta.get_field('name').max_length
        self.assertEquals(max_length, 100)

    def test_symbol_label(self):
        currency = Currency.objects.get(id=1)
        field_label = currency._meta.get_field('symbol').verbose_name
        self.assertEquals(field_label, 'symbol')

    def test_symbol_max_length(self):
        currency = Currency.objects.get(id=1)
        max_length = currency._meta.get_field('symbol').max_length
        self.assertEquals(max_length, 2)

    def test_language_label(self):
        currency = Currency.objects.get(id=1)
        field_label = currency._meta.get_field('language').verbose_name
        self.assertEquals(field_label, 'language')

    def test_language_max_length(self):
        currency = Currency.objects.get(id=1)
        max_length = currency._meta.get_field('language').max_length
        self.assertEquals(max_length, 2)

    def test_object_name_is_code(self):
        currency = Currency.objects.get(id=1)
        self.assertEquals(currency.code, str(currency))


class ExchangeRateModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        Currency.objects.create(code='EUR', name='Euro', symbol='€', language='de')
        Currency.objects.create(code='PLN', name='Polski złoty', symbol='zł', language='pl')
        ExchangeRate.objects.create(base_currency_id=1, target_currency_id=2, rate=0.8)
        ExchangeRate.objects.create(base_currency_id=1, target_currency_id=3, rate=4)

        cls.request = RequestFactory().get('/')
        cls.request.LANGUAGE_CODE = 'pl'

        cls.user = User.objects.create_user(username='testuser', password='12345')

        ProductCategory.objects.create(name='test_category')
        Product.objects.create(name='test_product', price=Decimal('100.00'), category_id=1)

    def test_exchange_rate(self):
        exchange_rate = ExchangeRate.objects.get(id=1)
        self.assertEquals(exchange_rate.rate, Decimal('0.8'))

    def test_get_user_currency_and_converted_product_price(self):
        product = Product.objects.get(id=1)
        currency = Currency.objects.get(code='PLN')
        user_currency, converted_product_price = ExchangeRate.get_user_currency_and_converted_product_price(self.request, product)

        self.assertEquals(user_currency, currency)
        self.assertEquals(converted_product_price, Decimal('400.00'))

    def test_convert_to_base_currency(self):
        amount = 100
        currency = Currency.objects.get(id=2)
        converted_amount = ExchangeRate.convert_to_base_currency(amount, currency)
        self.assertEquals(converted_amount, Decimal('125.00'))

    def test_convert_from_user_to_base(self):
        converted_price = 100
        original_price = ExchangeRate.convert_from_user_to_base(self.request, converted_price)
        self.assertEquals(original_price, 25)      # 100 PLN to USD

    def test_convert_to_user_currency(self):
        price = 100
        converted_price = ExchangeRate.convert_to_user_currency(self.request, price)
        self.assertEquals(converted_price, 400)      # 100 USD to PLN

