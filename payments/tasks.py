from time import sleep

from celery import shared_task


@shared_task(bind=True)
def send_report(self):
    print("Sending report...")
    return 'Report sent.'
