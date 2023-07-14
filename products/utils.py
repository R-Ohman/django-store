def change_product_visibility(queryset):
    for obj in queryset:
        obj.is_visible = not obj.is_visible
        obj.save()
    return None