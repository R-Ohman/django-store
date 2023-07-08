from django.contrib import admin

from products.models import ProductCategory, Product, Basket

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category')
    fields = ('image', 'name', 'description', ('price', 'quantity'), 'category')
    # readonly_fields = ('description',)
    ordering = ('name', 'price')
    search_fields = ('name',)


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'add_datetime')
    readonly_fields = ('add_datetime',)
    extra = 0

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)
    search_fields = ('name',)