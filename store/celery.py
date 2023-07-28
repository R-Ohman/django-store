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
    'send-report-every-single-minute': {
        'task': 'payments.tasks.send_report',
        'schedule': 60.0,
    },
    'send-user-invite-2-times-a-day': {
        'task': 'users.tasks.invite_users_to_visit',
        'schedule': 60.0,
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
