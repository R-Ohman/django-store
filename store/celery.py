from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from payments.tasks import update_exchange_rates_task, hello_world


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
app = Celery('store')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'update_exchange_rates': {
        'task': 'payments.tasks.update_exchange_rates_task',
        'schedule': 60,
    },
    'hello_world': {
        'task': 'payments.tasks.hello_world',
        'schedule': 17,
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')