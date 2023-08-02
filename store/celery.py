from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')

app = Celery('store')
app.conf.enable_utc = False
app.conf.update(timezone=settings.CELERY_TIMEZONE)

app.config_from_object(settings, namespace='CELERY')

# Celery beat settings
app.conf.beat_schedule = {
    'send-user-invite-2-times-a-day': {
        'task': 'users.tasks.invite_users_to_visit',
        'schedule': crontab(minute=0, hour='*/12')
    },
    'send-admin-unavailable-products-2-times-a-day': {
        'task': 'products.tasks.check_products_availability',
        'schedule': crontab(day_of_week='*', hour='*/12'),
    },
    'update-discounts-every-6-hours': {
        'task': 'products.tasks.check_expired_discounts',
        'schedule': crontab(minute=0, hour='*/6')
    },
    'cancel-unpaid-payments-every-2-hours': {
        'task': 'products.tasks.check_overdue_payments',
        'schedule': crontab(minute=0, hour='*/2')
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
