from django.contrib import admin

from payments.models import Currency, ExchangeRate
from payments.utils import update_exchange_rates, get_current_exchange_rate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'language',)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('target_currency', 'base_currency', 'rate', 'current_rate', 'updated')

    def run_update_exchange_rates(modeladmin, request, queryset):
        update_exchange_rates(queryset)
    run_update_exchange_rates.short_description = "Update exchange rates"

    def current_rate(self, obj):
        rate = get_current_exchange_rate(obj.target_currency.code)
        return f'{rate:.2f}'

    current_rate.short_description = 'Current Exchange Rate'

    actions = [run_update_exchange_rates]

