import requests

from payments.models import Currency, ExchangeRate
from store.settings import BASE_CURRENCY


def update_exchange_rates(exchange_rates_queryset=None):
    url = "https://api.exchangerate.host/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rates = data.get('rates')

    for exchange_rate in exchange_rates_queryset:
        rate = rates[exchange_rate.target_currency.code] / rates[exchange_rate.base_currency.code]
        exchange_rate.rate = rate
        exchange_rate.save()



def get_current_exchange_rate(targer_currency_code):
    base_currency = Currency.objects.get(code=BASE_CURRENCY)
    url = "https://api.exchangerate.host/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rates = data.get('rates')
        rate = rates[targer_currency_code] / rates[base_currency.code]

        return rate