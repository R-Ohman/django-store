import decimal

from django.db import models
from django.utils import timezone

from comments.models import ProductComment
from products.utils import round_number
from store.settings import BASE_CURRENCY


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class UserProductsQuerySet(models.QuerySet):
    def total_sum(self):
        for item in self:
            print(item.sum)

        return round_number(sum(float(item.sum.replace(',', ''))
                            if isinstance(item.sum, str) else item.sum for item in self))

    def total_quantity(self):
        return sum(item.quantity for item in self)

    def currency(self):
        return self[0].currency if self else BASE_CURRENCY


class Product(models.Model):
    name = models.CharField(max_length=256, unique=True, blank=True)
    image = models.ImageField(upload_to='products_images', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)  # price in default currency (USD)
    quantity = models.PositiveIntegerField(default=0)  # quantity in stock

    category = models.ForeignKey('products.ProductCategory', on_delete=models.CASCADE, null=True)
    is_visible = models.BooleanField(default=True)

    discount_percentage = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    discount_end_date = models.DateTimeField(blank=True, null=True)

    _original_quantity = None

    def __str__(self):
        return f'{self.category.name} | {self.name}'

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    @property
    def assessment(self):
        assessments = [object.assessment for object in ProductComment.objects.filter(product=self)]
        average = round(sum(assessments) / len(assessments), 1) if assessments else 0
        return average

    @property
    def comments(self):
        return ProductComment.objects.filter(product=self)

    @property
    def carousel_images(self):
        carousel = ProductCarousel.objects.get(product=self)
        return CarouselImage.objects.filter(carousel=carousel) if carousel else None

    @property
    def discounted_price(self):
        return self.discount_multiply(self.price)

    @property
    def discounted_price_str(self):
        return f'{round_number(self.discounted_price)} $'

    @property
    def discount(self):
        return f'-{int(self.discount_percentage)} %' if self.discount_is_active else ''


    @property
    def discount_is_active(self):
        return (self.discount_percentage and timezone.now() <= self.discount_end_date or
                self.discount_percentage and not self.discount_end_date)

    def discount_multiply(self, num):

        discount_percentage = self.discount_percentage if self.discount_is_active else 0

        discount_decimal = decimal.Decimal(discount_percentage) / 100
        num_decimal = decimal.Decimal(num)
        discounted_price = (1 - discount_decimal) * num_decimal

        return round(2 * discounted_price) / 2

    @property
    def time_to_discount_expiration(self):
        if self.discount_end_date:
            time_difference = self.discount_end_date - timezone.now()

            total_seconds = time_difference.total_seconds() if self.discount_is_active else 0

            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if days >= 1:
                # "DD:HH:MM:SS"
                return f"{int(days):02d}:{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            else:
                # "HH:MM:SS"
                return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        return None

    @property
    def delete_discount(self):
        if self.discount_percentage or self.discount_end_date:
            self.discount_end_date = None
            self.discount_percentage = None
            self.save()
            return True
        return False



class Basket(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    currency = models.ForeignKey('payments.Currency', on_delete=models.CASCADE, default=1)

    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # price in currency

    add_datetime = models.DateTimeField(auto_now_add=True)
    objects = UserProductsQuerySet.as_manager()

    def __str__(self):
        return f'{self.user.username} | {self.product.name}'

    @property
    def sum_without_discount(self):
        return round_number(self.quantity * self.price)

    @property
    def discounted_price(self):
        return self.product.discount_multiply(self.price)


    @property
    def sum(self):
        return round_number(self.quantity * self.discounted_price)


class Carousel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarouselImage(models.Model):
    carousel = models.ForeignKey('products.Carousel', on_delete=models.CASCADE, related_name='carousel_images')
    image = models.ImageField(upload_to='carousel_images/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.carousel.name + ' | ' + str(self.id)


class ProductCarousel(Carousel):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='product_carousel')

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.product.name
        super(ProductCarousel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name + ' | ' + self.product.name

    class Meta:
        verbose_name = 'product carousel'
        verbose_name_plural = 'product carousels'


class ProductFollower(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} | {self.product.name}'

