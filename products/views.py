import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from products.models import ProductCategory, Product, Basket
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from store.settings import LOGIN_URL


def index(request):
    context = {
        'title': 'Главная',
        'is_promotion': False,
    }
    return render(request, 'products/index.html', context)

def products(request):
    context = {
        'title': 'Каталог',
        'products' : Product.objects.all(),
        'categories' : ProductCategory.objects.all(),
    }

    return render(request, 'products/products.html', context)

@login_required(login_url=LOGIN_URL)
def add_product(request, product_id):
    basket = Basket.objects.filter(user=request.user, product_id=product_id).first()
    if basket:
        basket.quantity += 1
        basket.save()
    else:
        Basket.objects.create(user=request.user, product_id=product_id, quantity=1)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def delete_busket(request, id):
    basket = Basket.objects.get(id=id)
    basket.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def basket_update(request, id):
    if request.method == 'POST':
        basket = Basket.objects.get(id=id)
        json_data = json.loads(request.body.decode('utf-8'))
        quantity = int(json_data['quantity'])

        if quantity <= 0:
            # Если новое значение quantity меньше или равно 0, вернуть предыдущее значение
            response_data = {
                'success': False,
                'message': 'Недопустимое значение количества',
                'quantity': basket.quantity,
            }
        else:
            # Обновить значение quantity и сохранить корзину
            basket.quantity = quantity
            basket.save()
            baskets = Basket.objects.filter(user=request.user)
            response_data = {
                'success': True,
                'total_sum': float(baskets.total_sum()),
                'total_quantity': baskets.total_quantity(),
                'product_sum': float(basket.sum()),
            }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'success': False, 'message': 'Недопустимый запрос'})
