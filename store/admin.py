from django.contrib import admin

def set_admin_settings():
    admin.site.site_header = 'Store Administration'
    admin.site.site_title = 'Store Admin'
    admin.site.index_title = 'Welcome to Store Admin Panel'
