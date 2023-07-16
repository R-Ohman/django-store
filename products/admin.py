from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from products.forms import ProductAdminForm
from products.models import ProductCategory, Product, Basket, Carousel, CarouselImage
from products.utils import change_product_visibility
from store import settings
from store.admin import set_admin_settings


set_admin_settings()


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    lang_codes = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']

    # Создаем список полей, которые нужно отобразить в одной строке
    name_fields = [f'name_{lang_code}' for lang_code in lang_codes]
    description_fields = [f'description_{lang_code}' for lang_code in lang_codes]

    list_display = ('name', 'price', 'quantity', 'category', 'id' ,'is_visible',)
    fieldsets = (
        (None, {
            'fields': (('image', 'is_visible'),),
        }),
        ('English', {
            'fields': ('name_en', 'description_en'),
        }),
        ('Details', {
            'fields': ('price', 'quantity', 'category'),
            'classes': ('wide',),
        }),
        ('Translations', {
            'fields': ((*name_fields,), (*description_fields,)),
            'classes': ('collapse',),
        }),
    )

    ordering = ('name', 'price')
    search_fields = ('name',)
    form = ProductAdminForm

    def change_visibility(modeladmin, request, queryset):
        change_product_visibility(queryset)
    change_visibility.short_description = "Change visibility"

    actions = (change_visibility,)


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

    fieldsets = (
        (None, {
            'fields': (('name_en', 'description_en'),),
            'classes': ('wide',),
        }),
        ('Translations', {
            'fields': (tuple(name_fields), tuple(description_fields)),
            'classes': ('collapse',),
        }),
    )


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'add_datetime')
    readonly_fields = ('add_datetime',)
    extra = 0


admin.site.register(Carousel)
admin.site.register(CarouselImage)