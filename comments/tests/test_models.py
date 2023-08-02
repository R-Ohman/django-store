from django.test import TestCase
from decimal import Decimal
from comments.models import ProductComment, Attachment, Like, UserReport
from products.models import ProductCategory, Product
from users.models import User

from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile


class ProductCommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='testpassword')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(name='test product', category_id=1, price=Decimal('100.00'))

        cls.comment = ProductComment.objects.create(
            user_id=1,
            product_id=1,
            assessment=3.0,
            text='test text'
        )

    def test_comment_str(self):
        self.assertEqual(str(self.comment), 'test product | testuser | 3.0')

    def test_attachments(self):
        attachments = self.comment.attachments
        self.assertEqual(attachments.count(), 0)

    def test_assessment(self):
        self.assertEqual(self.comment.assessment, Decimal('3.0'))

    def test_rating(self):
        self.assertEqual(self.comment.rating, 0)

    def test_product_rating(self):
        product_average_assessment = self.comment.product.assessment
        self.assertEqual(product_average_assessment, Decimal('3.0'))

    def test_product_comments(self):
        product_comments = self.comment.product.comments
        self.assertEqual(product_comments.count(), 1)

    def test_comment_delete(self):
        self.comment.delete()

        product_comments = self.comment.product.comments
        self.assertEqual(product_comments.count(), 0)

        product_average_assessment = self.comment.product.assessment
        self.assertEqual(product_average_assessment, 0)


class AttachmentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='testpassword')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(name='test product', category_id=1, price=Decimal('100.00'))

        cls.comment = ProductComment.objects.create(
            user_id=1,
            product_id=1,
            assessment=3.0,
            text='test text'
        )

        fake_image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        fake_image.save(image_io, format='PNG')

        cls.attachment = Attachment.objects.create(
            comment_id=1,
            file=SimpleUploadedFile("fake_image.png", image_io.getvalue())
        )

    def test_attachment_file(self):
        self.assertTrue('/media/post_images/' in self.attachment.file.url)

    def test_attachment_delete(self):
        self.assertEqual(self.comment.attachments.count(), 1)
        self.attachment.delete()
        self.assertEqual(self.comment.attachments.count(), 0)


class LikeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='testpassword')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(name='test product', category_id=1, price=Decimal('100.00'))

        cls.comment = ProductComment.objects.create(
            user_id=1,
            product_id=1,
            assessment=3.0,
            text='test text'
        )

        cls.like = Like.objects.create(
            comment_id=1,
            user_id=1
        )

    def test_like_str(self):
        self.assertEqual(str(self.like), 'testuser | Comment: test product | testuser | 3.0')

    def test_create_unique(self):
        like = Like.objects.get_or_create(
            comment_id=1,
            user_id=1
        )
        self.assertEqual(like, (self.like, False))

    def test_like_delete(self):
        user = User.objects.get(id=1)
        self.assertEqual(self.like.user, user)

        self.assertEqual(user.likes.count(), 1)
        self.assertEqual(self.comment.likes.count(), 1)
        self.like.delete()
        self.assertEqual(self.comment.likes.count(), 0)
        self.assertEqual(user.likes.count(), 0)


class UserReportModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='testpassword')
        ProductCategory.objects.create(name='test category')
        Product.objects.create(name='test product', category_id=1, price=Decimal('100.00'))

        cls.comment = ProductComment.objects.create(
            user_id=1,
            product_id=1,
            assessment=3.0,
            text='test text'
        )

        cls.report = UserReport.objects.create(
            user_id=1,
            name='test name',
            email='email@test.com',
            topic='test topic',
            text='test text'
        )

    def test_report_str(self):
        self.assertEqual(str(self.report), 'email@test.com | test topic')

    def test_creation(self):
        user = User.objects.get(id=1)
        self.assertEqual(self.report.user, user)
        self.assertEqual(user.reports.count(), 1)
        self.assertEqual(self.report.is_resolved, False)


    def test_report_delete(self):
        user = User.objects.get(id=1)
        self.report.delete()
        self.assertEqual(user.reports.count(), 0)
