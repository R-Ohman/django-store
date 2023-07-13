from celery import Celery
import os

from store.settings import CELERY_BEAT_SCHEDULE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
app = Celery('store')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = CELERY_BEAT_SCHEDULE


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')