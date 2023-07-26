from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from orders.models import OrderItem, Refund, RefundProduct
from orders.models import Order
from orders.utils import update_refund_status_to_refunded


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'created')
    readonly_fields = ('sum_in_default_currency', 'created', 'order', 'sum_str', 'product')
    ordering = ('-id',)
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'created')
        }),
        ('Product Information', {
            'fields': ('product', 'quantity', 'price')
        }),
        ('Calculated Information', {
            'fields': ('sum_str', 'sum_in_default_currency')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price', 'get_currency', 'created')
    readonly_fields = ('created', 'get_currency')
    extra = 0

    def get_currency(self, obj):
        return obj.order.currency
    get_currency.short_description = 'Currency'



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('email', 'updated', 'status', 'sum_in_default_currency')
    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'status'),
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', ('address', 'phone'), ('postal_code', 'country')),
        }),
        ('Payment Details', {
            'fields': ('sum_str', 'sum_in_default_currency', 'created', 'updated'),
        }),
    )
    readonly_fields = ('user', 'first_name', 'last_name', 'email', 'phone', 'country',
                       'sum_in_default_currency', 'created', 'updated', 'sum_str',)
    ordering = ('-id',)
    inlines = (OrderItemInline,)


class OrderInline(admin.StackedInline):
    model = Order
    fields = ('id', 'status', 'email', 'address', 'created', 'updated', 'products_info')
    readonly_fields = ('id', 'email', 'created', 'address', 'updated', 'products_info')
    extra = 0
    ordering = ('-created',)
    classes = ('collapse',)

    def products_info(self, instance):
        order_items = OrderItem.objects.filter(order=instance)
        products = [f"{order_item.quantity} | {order_item.product.name}" for order_item in order_items]
        return '\n'.join(products)

    products_info.short_description = 'Products'


class RefundProductInline(admin.TabularInline):
    model = RefundProduct
    extra = 0
    readonly_fields = ('ordered_product', 'quantity',)
    fields = ('ordered_product', 'quantity', 'reason')
    classes = ('collapse',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'created', 'status', 'sum_in_default_currency')
    readonly_fields = ('order', 'created', 'sum_str', 'sum_in_default_currency', 'get_images')
    ordering = ('-id',)
    fieldsets = (
        ('Refund Details', {
            'fields': ('order', 'created', 'status', 'message'),
        }),
        ('Payment Details', {
            'fields': ('sum_str', 'sum_in_default_currency',),
        }),
        ('Attachments', {
            'fields': ('get_images', ),
            'classes': ('collapse',),
        }),
    )

    def run_update_refund_status(modeladmin, request, queryset):
        update_refund_status_to_refunded(queryset)

    run_update_refund_status.short_description = "Set refund status to refunded"
    actions = (run_update_refund_status,)
    def get_images(self, obj):
        return format_html(''.join([f'<img src="{attachment.file.url}" width="500" style="margin:10px;" alt="{attachment.file.url}" />' for attachment in obj.attachments.all()]))

    get_images.short_description = 'Images'


    classes = ('collapse',)
    extra = 0
    inlines = (RefundProductInline,)



@admin.register(RefundProduct)
class RefundProductAdmin(admin.ModelAdmin):
    list_display = ('refund', 'ordered_product', 'quantity')
    readonly_fields = ('refund', 'ordered_product', 'quantity')
    ordering = ('-id',)
    fieldsets = (
        ('Refund Details', {
            'fields': ('refund', 'ordered_product', 'quantity', 'reason'),
        }),
    )
    classes = ('collapse',)
    extra = 0
