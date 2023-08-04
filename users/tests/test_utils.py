from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse

from orders.models import OrderItem, Order
from payments.models import Currency
from products.models import ProductCategory, Product
from users import utils, translator
from users.models import User


class UsersUtilsTest(TestCase):
    def test_user_ip_exists(self):
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='46.204.55.255')
        country_code = utils.get_user_country(request)

        self.assertEqual(country_code, 'PL')

    def test_user_ip_not_exists(self):
        factory = RequestFactory()
        request = factory.get('/')
        country_code = utils.get_user_country(request)

        self.assertEqual(country_code, 'en')

    def test_user_empty_ip(self):
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='')
        country_code = utils.get_user_country(request)

        self.assertEqual(country_code, 'en')

    def test_invalid_ip(self):
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='invalid ip')
        with self.assertRaises(ValueError) as context:
            utils.get_user_country(request)

        self.assertIn("'invalid ip' does not appear to be an IPv4 or IPv6 address", str(context.exception))

    def test_referer_has_keyword(self):
        factory = RequestFactory()
        referer = reverse('user:registration')
        request = factory.get('/', HTTP_REFERER=referer)

        self.assertFalse(utils.check_referer_no_keywords(request))

    def test_referer_has_no_keyword(self):
        factory = RequestFactory()
        referer = reverse('index')
        request = factory.get('/', HTTP_REFERER=referer)

        self.assertTrue(utils.check_referer_no_keywords(request))

    def test_referer_has_no_keyword_empty_referer(self):
        request = RequestFactory().get('/', HTTP_REFERER='')
        self.assertTrue(utils.check_referer_no_keywords(request))

    def test_user_received_product(self):
        request = self.client.get('/')
        ProductCategory.objects.create(name='test category')
        product = Product.objects.create(
            name='test product',
            category_id=1,
            price=100,
        )
        request.user = User.objects.create(
            username='test username',
            password='test password',
        )
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        Order.objects.create(
            user_id=1,
            currency_id=1,
            address='test address',
            phone='+380000000000',
            status=Order.COMPLETED,
            email='test@email.com',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='00000',
        )
        OrderItem.objects.create(
            order_id=1,
            product_id=1,
            quantity=1,
            price=100,
        )
        self.assertTrue(utils.user_received_product(request, product))

    def test_user_received_product_false_order_not_completed(self):
        request = self.client.get('/')
        ProductCategory.objects.create(name='test category')
        product = Product.objects.create(
            name='test product',
            category_id=1,
            price=100,
        )
        request.user = User.objects.create(
            username='test username',
            password='test password',
        )
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        Order.objects.create(
            user_id=1,
            currency_id=1,
            address='test address',
            phone='+380000000000',
            status=Order.PROCEEDED,
            email='test@email.com',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='00000',
        )
        OrderItem.objects.create(
            order_id=1,
            product_id=1,
            quantity=1,
            price=100,
        )
        self.assertFalse(utils.user_received_product(request, product))

    def test_user_received_product_false_empty_order(self):
        request = self.client.get('/')
        ProductCategory.objects.create(name='test category')
        product = Product.objects.create(
            name='test product',
            category_id=1,
            price=100,
        )
        request.user = User.objects.create(
            username='test username',
            password='test password',
        )
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        Order.objects.create(
            user_id=1,
            currency_id=1,
            address='test address',
            phone='+380000000000',
            status=Order.COMPLETED,
            email='test@email.com',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='00000',
        )
        self.assertFalse(utils.user_received_product(request, product))

    def test_user_received_product_user_is_not_authenticated(self):
        request = self.client.get('/')
        ProductCategory.objects.create(name='test category')
        product = Product.objects.create(
            name='test product',
            category_id=1,
            price=100,
        )
        request.user = AnonymousUser()
        self.assertFalse(utils.user_received_product(request, product))


class UsersTranslatorTest(TestCase):
    def test_translate_text_to_user_language_pl(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.LANGUAGE_CODE = 'pl'
        translated_text = translator.translate_text_to_user_language('Hello world', request)
        self.assertEqual(translated_text, 'Witaj świecie')

    def test_translate_text_to_user_language_en(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.LANGUAGE_CODE = 'en'
        translated_text = translator.translate_text_to_user_language('Hello world', request)
        self.assertEqual(translated_text, 'Hello world')

    def test_translate_text_to_language_pl(self):
        language_code = 'pl'
        translated_text = translator.translate_text_to_language('Hello world', language_code)
        self.assertEqual(translated_text, 'Witaj świecie')

    def test_translate_text_to_language_en(self):
        language_code = 'en'
        translated_text = translator.translate_text_to_language('Hello world', language_code)
        self.assertEqual(translated_text, 'Hello world')

    def test_translate_text_to_language_by_currency_pln(self):
        currency = Currency.objects.create(code='PLN', name='Polish Zloty', symbol='zł', language='pl')
        translated_text = translator.translate_text_to_language_by_currency('Hello world', currency)
        self.assertEqual(translated_text, 'Witaj świecie')

    def test_translate_text_to_language_by_currency_usd(self):
        currency = Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        translated_text = translator.translate_text_to_language_by_currency('Hello world', currency)
        self.assertEqual(translated_text, 'Hello world')
