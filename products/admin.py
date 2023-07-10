from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from products.forms import ProductAdminForm
from products.models import ProductCategory, Product, Basket



@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'category')
    fields = ('image', 'name', 'description', ('price', 'quantity'), 'category')
    ordering = ('name', 'price')
    search_fields = ('name',)
    form = ProductAdminForm


@admin.register(ProductCategory)
class ProductCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)
    search_fields = ('name',)


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'add_datetime')
    readonly_fields = ('add_datetime',)
    extra = 0

