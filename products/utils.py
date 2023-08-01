
def change_product_visibility(queryset):
    invisible_products = []
    for obj in queryset:
        obj.is_visible = not obj.is_visible
        if not obj.is_visible:
            invisible_products.append(obj)
        obj.save()
    return invisible_products


def round_number(num):
    """
        '{:,.2f}'.format(num)
    """
    #num = round(num * 2) / 2
    return '{:,.2f}'.format(num)

def number_to_float(num_str):
    num_str = num_str.replace(',', '')
    num_float = float(num_str)
    return num_float


