from django.contrib import admin
from users.models import User, Order
from products.models import OrderItem

class OrderInline(admin.StackedInline):
    model = Order
    fields = ('id', 'status', ('email', 'address'), ('created', 'updated'), 'products_info')
    readonly_fields = ('id', 'email', 'created', 'address', 'updated', 'products_info')
    extra = 0
    ordering = ('-created',)


    def products_info(self, instance):
        order_items = OrderItem.objects.filter(order=instance)
        products = [f"{order_item.quantity} | {order_item.product.name}" for order_item in order_items]
        return '\n'.join(products)

    products_info.short_description = 'Products'


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    fields = ('username', ('first_name', 'last_name'), 'email', ('is_staff', 'is_active', 'is_superuser'),
              ('groups', 'user_permissions'), 'password', ('last_login', 'date_joined'))
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('username',)
    inlines = (OrderInline,)


admin.site.register(User, UserAdmin)
