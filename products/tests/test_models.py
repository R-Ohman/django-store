from django.test import TestCase
from decimal import Decimal

from django.utils import timezone

from payments.models import Currency
from products.models import Product, ProductCategory, Basket, Carousel, ProductCarousel, CarouselImage, ProductFollower
from users.models import User

from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile


class ProductCategoryModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = ProductCategory.objects.create(name='TestCategory')

    def test_product_category_creation(self):
        self.assertEqual(str(self.category), 'TestCategory')
        self.assertEqual(self.category.description, None)

    def test_product_category_delete(self):
        self.assertEqual(ProductCategory.objects.count(), 1)
        self.category.delete()
        self.assertEqual(ProductCategory.objects.count(), 0)


class ProductModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = ProductCategory.objects.create(name='TestCategory')
        cls.product = Product.objects.create(
            name='TestProduct',
            price=Decimal('10.00'),
            quantity=5,
            category=cls.category,
        )

    def test_product_creation(self):
        self.assertEqual(str(self.product), f'{self.category.name} | {self.product.name}')
        self.assertEqual(self.product.assessment, 0)
        self.assertEqual(self.product.quantity, 5)
        self.assertEqual(str(self.product.category), 'TestCategory')
        self.assertEqual(self.product.comments.count(), 0)
        self.assertEqual(self.product.product_carousel.count(), 0)

    def test_fields(self):
        max_length = self.product._meta.get_field('name').max_length
        self.assertEquals(max_length, 128)
        max_digits = self.product._meta.get_field('price').max_digits
        self.assertEquals(max_digits, 7)

    def test_discount(self):
        self.assertFalse(self.product.discount_is_active)
        self.assertEqual(self.product.discounted_price, Decimal('10.00'))
        self.assertEqual(self.product.discounted_price_str, '10.00 $')
        self.assertEqual(self.product.discount_multiply(10), Decimal('10.00'))
        self.assertEqual(self.product.discount, '')
        self.assertEqual(self.product.time_to_discount_expiration, None)

        self.product.discount_percentage = Decimal('25.0')
        self.product.save()

        self.assertTrue(self.product.discount_is_active)
        self.assertEqual(self.product.discount, '-25 %')
        self.assertEqual(self.product.discounted_price, Decimal('7.50'))
        self.assertEqual(self.product.discounted_price_str, '7.50 $')
        self.assertEqual(self.product.discount_multiply(10), Decimal('7.50'))

        self.product.discount_end_date = timezone.now() + timezone.timedelta(days=1)
        self.assertTrue(self.product.discount_is_active)

        self.product.discount_end_date = timezone.now() - timezone.timedelta(days=1)
        self.assertFalse(self.product.discount_is_active)

    def test_product_delete(self):
        self.assertEqual(Product.objects.count(), 1)
        self.product.delete()
        self.assertEqual(Product.objects.count(), 0)


class BasketModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user1', password='q1w2e3r4t5y')
        cls.category = ProductCategory.objects.create(name='TestCategory')
        cls.product = Product.objects.create(
            name='TestProduct',
            price=Decimal('10.00'),
            quantity=5,
            category=cls.category
        )
        cls.currency = Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        cls.basket = Basket.objects.create(
            user_id=1,
            product=cls.product,
            currency_id=1,
            quantity=2,
            price=Decimal('10.00')
        )

    def test_basket_creation(self):
        self.assertEqual(str(self.basket), f'user1 | {self.product.name}')
        self.assertEqual(self.basket.sum_without_discount, '20.00')
        self.assertEqual(self.basket.sum, '20.00')
        self.assertEqual(self.basket.discounted_price, Decimal('10.00'))

    def test_basket_delete(self):
        self.assertEqual(Basket.objects.count(), 1)
        self.basket.delete()
        self.assertEqual(Basket.objects.count(), 0)


class CarouselModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.carousel = Carousel.objects.create(name='TestCarousel')

    def test_carousel_creation(self):
        self.assertEqual(str(self.carousel), 'TestCarousel')
        self.assertEqual(self.carousel.description, '')

    def test_carousel_delete(self):
        self.assertEqual(Carousel.objects.count(), 1)
        self.carousel.delete()
        self.assertEqual(Carousel.objects.count(), 0)


class CarouselImageModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = ProductCategory.objects.create(name='TestCategory')
        cls.product = Product.objects.create(
            name='TestProduct',
            price=Decimal('10.00'),
            quantity=5,
            category=cls.category
        )
        cls.carousel = ProductCarousel.objects.create(
            name='TestProductCarousel',
            product=cls.product
        )

        fake_image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        fake_image.save(image_io, format='PNG')

        cls.carousel_image = CarouselImage.objects.create(
            carousel=cls.carousel,
            image=SimpleUploadedFile('test_image.jpg', image_io.getvalue()),
        )

    def test_carousel_image_creation(self):
        self.assertEqual(str(self.carousel_image), 'TestProductCarousel | 1')
        self.assertEqual(self.carousel_image.carousel, self.carousel)
        self.assertTrue('/media/carousel_images/test_image' in self.carousel_image.image.url)
        self.assertEqual(self.carousel_image.caption, '')

    def test_carousel_image_delete(self):
        self.assertEqual(self.carousel.carousel_images.count(), 1)
        self.carousel_image.delete()
        self.assertEqual(self.carousel.carousel_images.count(), 0)


class ProductCarouselModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = ProductCategory.objects.create(name='TestCategory')
        cls.product = Product.objects.create(
            name='TestProduct',
            price=Decimal('10.00'),
            quantity=5,
            category=cls.category,
            is_visible=True
        )
        cls.carousel = ProductCarousel.objects.create(
            product=cls.product
        )

    def test_product_carousel_creation(self):
        self.assertEqual(str(self.carousel), 'Carousel TestProduct')
        self.assertEqual(self.carousel.name, 'TestProduct')
        self.assertEqual(self.carousel.product, self.product)

    def test_product_carousel_delete(self):
        self.assertEqual(self.product.product_carousel.count(), 1)
        self.carousel.delete()
        self.assertEqual(self.product.product_carousel.count(), 0)


class ProductFollowerModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user', password='q1w2e3r4t5y')
        cls.category = ProductCategory.objects.create(name='TestCategory')
        cls.product = Product.objects.create(name='TestProduct', price=Decimal('10.00'),
                                              quantity=5, category=cls.category,)
        cls.product_follower = ProductFollower.objects.create(user=cls.user, product=cls.product)

    def test_product_follower_creation(self):
        self.assertEqual(str(self.product_follower), 'test_user | TestProduct')
        self.assertEqual(self.product_follower.user, self.user)
        self.assertEqual(self.product_follower.product, self.product)

    def test_product_follower_delete(self):
        self.assertEqual(self.product.product_followers.count(), 1)
        self.product_follower.delete()
        self.assertEqual(self.product.product_followers.count(), 0)
