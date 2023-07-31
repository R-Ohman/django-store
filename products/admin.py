from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from comments.admin import CommentInline, AttachmentInline
from products.forms import ProductAdminForm
from products.models import ProductCategory, Product, Basket, Carousel, CarouselImage, ProductCarousel, ProductFollower
from products.utils import change_product_visibility
from store import settings
from store.admin import set_admin_settings


set_admin_settings()


class CarouselImageInline(admin.TabularInline):
    model = CarouselImage
    extra = 0
    readonly_fields = ('file_preview',)
    fields = ('image', 'file_preview', 'caption')

    def file_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150">', obj.image.url)
        return ''

    file_preview.short_description = 'Image Preview'


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_carousel_images_number')
    ordering = ('name',)
    search_fields = ('name',)

    def get_carousel_images_number(self, obj):
        return obj.carousel_images.count()
    get_carousel_images_number.short_description = 'Images'
    inlines = (CarouselImageInline,)


class ProductCarouselInline(admin.StackedInline):
    model = ProductCarousel
    extra = 0
    readonly_fields = ('get_images',)
    fields = ('name', 'description', 'product', 'get_images')

    def get_images(self, obj):
        images = obj.carousel_images.all()
        url = reverse('admin:products_carousel_change', args=[obj.pk])
        images_html = f'<a href="{url}">Click to go to the carousel preview.</a><br/>'
        images_html += ''.join(f'<img src="{image.image.url}" width="200" style="margin:10px;"/>' for image in images)
        return format_html(f'<a href="{url}">{images_html}</a>')
    get_images.short_description = 'Images'
    classes = ('collapse',)


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    lang_codes = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']

    # Создаем список полей, которые нужно отобразить в одной строке
    name_fields = [f'name_{lang_code}' for lang_code in lang_codes]
    description_fields = [f'description_{lang_code}' for lang_code in lang_codes]

    list_display = ('name', 'price', 'discount_percentage', 'quantity', 'category', 'id' ,'is_visible',)
    fieldsets = (
        (None, {
            'fields': (('image', 'is_visible'),),
        }),
        ('English', {
            'fields': ('name_en', 'description_en'),
        }),
        ('Details', {
            'fields': ('price', ('discount_percentage', 'discount_end_date'), 'quantity', 'category'),
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
    inlines = (ProductCarouselInline, CommentInline,)


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


@admin.register(ProductFollower)
class ProductFollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created')
    ordering = ('user',)
    search_fields = ('product',)
    fields = ('user', 'product', 'created')
    readonly_fields = ('user', 'product', 'created')
