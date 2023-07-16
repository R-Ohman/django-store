def change_product_visibility(queryset):
    for obj in queryset:
        obj.is_visible = not obj.is_visible
        obj.save()
    return


def round_number(num):
    """
        Round number to 0.5
        Set decimal places to 2
    """
    num = round(num * 2) / 2
    return '{:,.2f}'.format(num)