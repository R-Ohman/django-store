from django.test import TestCase
from orders.models import Order, OrderItem, Refund, RefundProduct, RefundAttachment
from payments.models import Currency
from products.models import ProductCategory, Product
from users.models import User
from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='12345')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')

        Order.objects.create(
            user=User.objects.get(id=1),
            currency=Currency.objects.get(id=1),
            address='test address',
            email='test email',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='12345',
            phone='+1234567890'
        )

    def test_creation(self):
        order = Order.objects.get(id=1)

        self.assertEqual(order.user.username, 'testuser')
        self.assertTrue(order.is_active)
        self.assertEqual(order.status, order.FORMING)

    def test_refund(self):
        order = Order.objects.get(id=1)
        self.assertFalse(order.refund_exists)

    def test_can_refund(self):
        order = Order.objects.get(id=1)
        self.assertFalse(order.can_refund)

        order.status = order.PROCEEDED
        self.assertTrue(order.can_refund)

    def test_delete(self):
        order = Order.objects.get(id=1)
        order.delete()
        self.assertFalse(Order.objects.filter(id=1).exists())


class OrderItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='12345')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(
            name='test product',
            category=ProductCategory.objects.get(id=1),
            price=100,
            quantity=1,
            description='test description'
        )
        Order.objects.create(
            user=User.objects.get(id=1),
            currency=Currency.objects.get(id=1),
            address='test address',
            email='test email',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='12345',
            phone='+1234567890'
        )
        OrderItem.objects.create(
            order=Order.objects.get(id=1),
            product=Product.objects.get(id=1),
            quantity=1,
            price=100
        )

    def test_creation(self):
        order_item = OrderItem.objects.get(id=1)

        self.assertEqual(order_item.order.id, 1)
        self.assertEqual(order_item.product.id, 1)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.price, 100)

    def test_sum(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEqual(order_item.sum, 100)
        self.assertEqual(order_item.sum_str, '100.00 USD')

    def test_order_sum(self):
        order_item = OrderItem.objects.get(id=1)
        order = order_item.order
        self.assertEqual(order.sum, 100)
        self.assertEqual(order.sum_str, '100.00 USD')

    def test_order_item_delete(self):
        order_item = OrderItem.objects.get(id=1)
        self.assertEqual(order_item.order.order_items.count(), 1)
        order_item.delete()
        self.assertFalse(OrderItem.objects.filter(id=1).exists())
        self.assertEqual(order_item.order.order_items.count(), 0)


class RefundModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='12345')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(
            name='test product',
            category=ProductCategory.objects.get(id=1),
            price=100,
            quantity=1,
            description='test description'
        )
        Order.objects.create(
            user=User.objects.get(id=1),
            currency=Currency.objects.get(id=1),
            address='test address',
            email='test email',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='12345',
            phone='+1234567890',
            status=Order.PROCEEDED
        )
        OrderItem.objects.create(
            order=Order.objects.get(id=1),
            product=Product.objects.get(id=1),
            quantity=1,
            price=100
        )
        Refund.objects.create(
            order=Order.objects.get(id=1),
            message='test message'
        )

    def test_creation(self):
        refund = Refund.objects.get(id=1)

        self.assertEqual(refund.order.id, 1)
        self.assertEqual(refund.status, Refund.REFUND_REQUESTED)

    def test_refund_products(self):
        refund = Refund.objects.get(id=1)
        self.assertEqual(refund.refund_products.count(), 0)

        RefundProduct.objects.create(
            refund=refund,
            ordered_product=OrderItem.objects.get(id=1),
            quantity=1
        )
        self.assertEqual(refund.refund_products.count(), 1)

    def test_refund_attachments(self):
        refund = Refund.objects.get(id=1)
        self.assertEqual(refund.attachments.count(), 0)

        RefundAttachment.objects.create(
            refund=refund,
            file='test_file.jpg'
        )
        self.assertEqual(refund.attachments.count(), 1)

    def test_delete(self):
        refund = Refund.objects.get(id=1)
        refund.delete()
        self.assertFalse(Refund.objects.filter(id=1).exists())


class RefundProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='12345')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(
            name='test product',
            category=ProductCategory.objects.get(id=1),
            price=100,
            quantity=1,
            description='test description'
        )
        Order.objects.create(
            user=User.objects.get(id=1),
            currency=Currency.objects.get(id=1),
            address='test address',
            email='test email',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='12345',
            phone='+1234567890',
            status=Order.PROCEEDED
        )
        OrderItem.objects.create(
            order=Order.objects.get(id=1),
            product=Product.objects.get(id=1),
            quantity=1,
            price=100
        )
        Refund.objects.create(
            order=Order.objects.get(id=1),
            message='test message'
        )
        RefundProduct.objects.create(
            refund=Refund.objects.get(id=1),
            ordered_product=OrderItem.objects.get(id=1),
            quantity=1,
            reason='Defective Product'
        )

    def test_creation(self):
        refund_product = RefundProduct.objects.get(id=1)

        self.assertEqual(refund_product.refund.id, 1)
        self.assertEqual(refund_product.quantity, 1)
        self.assertEqual(refund_product.reason, 'Defective Product')

    def test_sum(self):
        refund_product = RefundProduct.objects.get(id=1)
        self.assertEqual(refund_product.sum, 100)

    def test_delete(self):
        refund_product = RefundProduct.objects.get(id=1)
        refund_product.delete()
        self.assertFalse(RefundProduct.objects.filter(id=1).exists())


class RefundAttachmentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='12345')
        Currency.objects.create(code='USD', name='US Dollar', symbol='$', language='en')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(
            name='test product',
            category=ProductCategory.objects.get(id=1),
            price=100,
            quantity=1,
            description='test description'
        )
        Order.objects.create(
            user=User.objects.get(id=1),
            currency=Currency.objects.get(id=1),
            address='test address',
            email='test email',
            first_name='test first name',
            last_name='test last name',
            country='US',
            postal_code='12345',
            phone='+1234567890',
            status=Order.PROCEEDED
        )
        OrderItem.objects.create(
            order=Order.objects.get(id=1),
            product=Product.objects.get(id=1),
            quantity=1,
            price=100
        )
        Refund.objects.create(
            order=Order.objects.get(id=1),
            message='test message',
            status=Refund.REFUND_REQUESTED
        )
        fake_image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        fake_image.save(image_io, format='PNG')

        RefundAttachment.objects.create(
            refund=Refund.objects.get(id=1),
            file=SimpleUploadedFile('test_file.jpg', image_io.getvalue())
        )

    def test_creation(self):
        refund_attachment = RefundAttachment.objects.get(id=1)

        self.assertEqual(refund_attachment.refund.id, 1)
        self.assertTrue('/media/refunds/test_file' in refund_attachment.file.url)

    def test_delete(self):
        refund_attachment = RefundAttachment.objects.get(id=1)
        refund_attachment.delete()
        self.assertFalse(RefundAttachment.objects.filter(id=1).exists())
