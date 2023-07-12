from django.contrib import admin

from orders.admin import OrderInline
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    fields = ('username', ('first_name', 'last_name'), 'email', ('is_staff', 'is_active', 'is_superuser'),
              ('groups', 'user_permissions'), 'password', ('last_login', 'date_joined'))
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('username',)
    inlines = (OrderInline,)


admin.site.register(User, UserAdmin)
