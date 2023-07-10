from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from products.forms import ProductAdminForm
from products.models import ProductCategory, Product, Basket, Currency, ExchangeRate
from store import settings


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    lang_codes = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']

    # Создаем список полей, которые нужно отобразить в одной строке
    name_fields = [f'name_{lang_code}' for lang_code in lang_codes]
    description_fields = [f'description_{lang_code}' for lang_code in lang_codes]

    list_display = ('name', 'price', 'quantity', 'category', 'id',)
    fields = (
        'image',
        'name_en', 'description_en',
        ('price', 'quantity', 'category',),
        (*name_fields,),
        (*description_fields,),
    )

    ordering = ('name', 'price')
    search_fields = ('name',)
    form = ProductAdminForm


@admin.register(ProductCategory)
class ProductCategoryAdmin(TranslationAdmin):
    lang_codes = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']

    # Создаем список полей, которые нужно отобразить в одной строке
    name_fields = [f'name_{lang_code}' for lang_code in lang_codes]
    description_fields = [f'description_{lang_code}' for lang_code in lang_codes]


    list_display = ('name', 'description', 'id',)
    ordering = ('name',)
    search_fields = ('name',)
    form = ProductAdminForm

    fields = (
        'name_en',
        'description_en',
        (*name_fields,),
        (*description_fields,),
    )



class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'add_datetime')
    readonly_fields = ('add_datetime',)
    extra = 0

admin.site.register(Currency)
admin.site.register(ExchangeRate)
