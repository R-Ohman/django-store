from time import sleep

from celery import shared_task
from django.utils import timezone
from products.models import Product


@shared_task(bind=True)
def hello_world(self):
    sleep(10)
    print("Hello world!")
    return None

@shared_task(bind=True)
def send_report(self):
    print("Sending report...")
    return 'Report sent.'


@shared_task(bind=True)
def check_products_quantity_and_discount(self):
    products = Product.objects.all(visible=True)
    for product in products:
        if product.quantity == 0:
            # senf email to admin
            product.is_visible = False
        if product.discount_end_date and product.discount_end_date >= timezone.now():
            product.discount_percentage = None
            product.discount_end_date = None

        product.save()
    return 'Products checked.'
