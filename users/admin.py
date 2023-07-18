from django.contrib import admin

from orders.admin import OrderInline
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_confirmed', 'date_joined')
    list_display_links = ('username', 'email')

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
        ('Personal Info', {
            'fields': (('first_name', 'last_name'), 'email'),
        }),
        ('Permissions', {
            'fields': (('is_staff', 'is_active', 'is_superuser', ),
                       ('is_confirmed', 'number_of_available_username_changes'),
                       ('groups', 'user_permissions')),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('username',)
    inlines = (OrderInline,)
