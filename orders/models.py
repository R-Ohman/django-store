import requests
from django.core.exceptions import ValidationError
from django.db import models
from django_countries.fields import CountryField
from datetime import timedelta
from django.utils.timezone import now

from products.models import UserProductsQuerySet
from store.settings import BASE_CURRENCY, REFUND_TIME
from payments.models import ExchangeRate
from phonenumber_field.modelfields import PhoneNumberField
from users.translator import translate_text_to_user_language


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'
    COMPLETED = 'CMP'

    STATUSES = (
        (FORMING, 'Forming'),
        (SENT_TO_PROCEED, 'Sent to proceed'),
        (PROCEEDED, 'Proceeded'),
        (PAID, 'Paid'),
        (READY, 'Ready'),
        (CANCEL, 'Canceled'),
        (COMPLETED, 'Completed'),
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    currency = models.ForeignKey('payments.Currency', on_delete=models.CASCADE, default=None)

    address = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True, db_index=True)
    email = models.EmailField(max_length=128)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, choices=STATUSES, default=FORMING)

    country = CountryField()
    postal_code = models.CharField(max_length=12)
    phone = PhoneNumberField(null=False, blank=False, unique=False)

    def __str__(self):
        return f'{self.id} | {self.email}'

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'

    @property
    def sum(self):
        order_items = OrderItem.objects.filter(order=self)
        total_sum = sum(item.sum for item in order_items)
        return total_sum

    @property
    def sum_str(self):
        return f'{self.sum} {self.currency.code}'

    def sum_in_default_currency(self, sum=None):
        if not sum:
            sum = self.sum
        converted_sum = ExchangeRate.convert_to_base_currency(sum, self.currency)
        converted_sum = round(converted_sum, 2)
        return f'{converted_sum} {BASE_CURRENCY}'

    @property
    def refund_friendly_statuses(self):
        return [self.PROCEEDED, self.PAID, self.READY, self.COMPLETED]

    @property
    def refund(self):
        try:
            return Refund.objects.get(order=self)
        except Refund.DoesNotExist:
            return None

    @property
    def refund_exists(self):
        return Refund.objects.filter(order=self).exists()

    @property
    def can_refund(self):
        current_time = now()
        time_difference = current_time - self.created
        return (
                time_difference < timedelta(days=REFUND_TIME)
                and self.status in self.refund_friendly_statuses
                and not self.refund_exists
        )


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)

    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)  # price in currency
    quantity = models.PositiveIntegerField(default=0)

    objects = UserProductsQuerySet.as_manager()

    def __str__(self):
        return f'{self.id} | {self.product.name}'

    class Meta:
        verbose_name = 'order item'
        verbose_name_plural = 'order items'

    @property
    def created(self):
        return self.order.created.strftime('%d-%m-%Y %H:%M:%S')

    @property
    def sum(self):
        return self.quantity * self.price

    @property
    def sum_str(self):
        return f'{self.sum} {self.order.currency.code}'

    def sum_in_default_currency(self):
        return self.order.sum_in_default_currency(self.sum)


class Refund(models.Model):
    REFUND_REQUESTED = 'RR'
    REFUNDED = 'RF'

    STATUSES = (
        (REFUND_REQUESTED, 'Refund requested'),
        (REFUNDED, 'Refunded'),
    )
    @staticmethod
    def get_reason_choices(request):
        if request is None:
            request = requests.Request()
            request.LANGUAGE_CODE = 'en'
        return [
            ('Defective Product', translate_text_to_user_language('Defective Product', request)),
            ('Wrong Product', translate_text_to_user_language('Wrong Product', request)),
            ('Received Damaged', translate_text_to_user_language('Received Damaged', request)),
            ('Other', translate_text_to_user_language('Other', request)),
        ]

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE)
    message = models.TextField(max_length=1024, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, choices=STATUSES, default=REFUND_REQUESTED)

    def __str__(self):
        return f'{self.order} | {dict(self.STATUSES)[self.status]}'

    class Meta:
        verbose_name = 'refund'
        verbose_name_plural = 'refunds'

    @property
    def refund_products(self):
        return RefundProduct.objects.filter(refund=self)

    @property
    def sum(self):
        return sum(item.sum for item in self.refund_products)

    @property
    def sum_str(self):
        return f'{self.sum} {self.order.currency.code}'

    @property
    def sum_in_default_currency(self):
        converted_sum = ExchangeRate.convert_to_base_currency(self.sum, self.order.currency)
        converted_sum = round(converted_sum, 2)
        return f'{converted_sum} {BASE_CURRENCY}'


class RefundProduct(models.Model):
    refund = models.ForeignKey('orders.Refund', on_delete=models.CASCADE)
    ordered_product = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=256, choices=Refund.get_reason_choices(None))

    def __str__(self):
        return f'{self.refund} | {self.ordered_product} | {self.quantity}'

    class Meta:
        verbose_name = 'refund product'
        verbose_name_plural = 'refund products'

    @staticmethod
    def get_ordered_products_choices(refund):
        ordered_products = OrderItem.objects.filter(order=refund.order)
        choices = [(item.id, str(item)) for item in ordered_products]
        return choices

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity should be greater than 0.")

        if self.quantity > self.ordered_product.quantity:
            raise ValidationError("Quantity exceeds the available quantity in the order.")

    def set_ordered_product_choices(self, refund):
        self._meta.get_field('ordered_product').choices = self.get_ordered_products_choices(refund)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self.set_ordered_product_choices(self.refund)

    @property
    def sum(self):
        return self.quantity * self.ordered_product.price



class RefundAttachment(models.Model):
    refund = models.ForeignKey('orders.Refund', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='refunds/', null=False, blank=False)

    def __str__(self):
        return f'{self.refund} | {self.file}'

    class Meta:
        verbose_name = 'refund attachment'
        verbose_name_plural = 'refund attachments'
