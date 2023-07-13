from celery import shared_task


@shared_task
def update_exchange_rates_task():
    from payments.utils import update_exchange_rates
    update_exchange_rates()
