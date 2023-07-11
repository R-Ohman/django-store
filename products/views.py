import json
from decimal import Decimal

from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from products.models import ProductCategory, Product, Basket, ExchangeRate, Currency
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from store.settings import LOGIN_URL
from store.translator import translate_text_to_user_language
from django.db import models


def index(request):
    context = {
        'title': translate_text_to_user_language('Homepage', request),
        'is_promotion': False,
    }

    return render(request, 'products/index.html', context)


def products(request, category_id=None, page=1):
    language_currency_dictionary = {
        'en': ('$', 'USD'),
        'uk': ('₴', 'UAH'),
        'pl': ('zł', 'PLN'),
    }
    user_currency = language_currency_dictionary[request.LANGUAGE_CODE]
    user_currency_id = Currency.objects.get(code=user_currency[1])
    default_currency_id = Currency.objects.get(code='USD')
    exchange_rate = ExchangeRate.objects.filter(base_currency=user_currency_id, target_currency=default_currency_id).first()

    products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
    products_with_converted_price = None
    if exchange_rate:
        # Конвертируем цены товаров в выбранную валюту
        products_with_converted_price = [
            {
                'product': product,
                'price': '{:.2f}'.format(round(Decimal(product.price) * Decimal(exchange_rate.rate) / Decimal('0.5')) * Decimal('0.5')),
                'currency': user_currency[0],
            }
            for product in products
        ]

    page = request.GET.get('page', 1)  # Получаем номер страницы из параметров запроса
    per_page = 3  # Количество продуктов на странице
    # Разбиваем продукты на страницы
    paginator = Paginator(products_with_converted_price, per_page)

    try:
        page_number = int(page)
        page_products = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_products = paginator.page(1)

    # Если это AJAX-запрос, возвращаем фрагмент HTML
    if request.is_ajax():
        context = {
            'products_with_converted_price': page_products,
            'current_page': int(page),
        }
        product_list_html = render_to_string('products/product_cards.html', context)
        page_list_html = render_to_string('products/pagination.html', context)
        return JsonResponse({
            'product_list_html': product_list_html,
            'page_list_html': page_list_html
            })

    # Возвращаем полный HTML для обычного запроса
    context = {
        'title': translate_text_to_user_language('Catalog', request),
        'products_with_converted_price': page_products,
        'categories': ProductCategory.objects.all(),
        'current_page': int(page),  # Добавляем текущую страницу в контекст
        'category': ProductCategory.objects.get(id=category_id) if category_id else None,
    }

    return render(request, 'products/products.html', context)


@login_required(login_url=LOGIN_URL)
def add_product(request, product_id):
    basket = Basket.objects.filter(user=request.user, product_id=product_id).first()

    response = {
        'success': True,
        'product_name': Product.objects.get(id=product_id).name,
    }

    if basket and basket.quantity < basket.product.quantity:
        basket.quantity += 1
        basket.save()
    elif not basket and Product.objects.get(id=product_id).quantity > 0:
        Basket.objects.create(user=request.user, product_id=product_id, quantity=1)
    else:
        response['success'] = False
        response['message'] = translate_text_to_user_language('Not enough goods in stock =(', request)

    return JsonResponse(response)


@login_required
def delete_basket(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    baskets = Basket.objects.filter(user=request.user)
    context = {
        'baskets': baskets,
        'total_sum': baskets.total_sum(),
        'total_quantity': baskets.total_quantity(),
    }

    basket_list_html = render_to_string('products/basket.html', context)

    return JsonResponse({'success': True, 'basket_list_html': basket_list_html})



@login_required
def basket_update(request, id):
    if request.method == 'POST':
        basket = Basket.objects.get(id=id)
        json_data = json.loads(request.body.decode('utf-8'))
        quantity = int(json_data['quantity']) if json_data['quantity'] else 0
        baskets = Basket.objects.filter(user=request.user)
        quantity_magazine = Product.objects.get(id=basket.product_id).quantity

        if 0 < quantity <= quantity_magazine:
            # Обновить значение quantity и сохранить корзину
            basket.quantity = quantity
            basket.save()
            response_data = {
                'success': True,
            }
        else:
            # Если новое значение quantity меньше или равно 0, вернуть предыдущее значение
            response_data = {
                'success': False,
                'message': translate_text_to_user_language('Unacceptable quantity value', request),
            }

        # basket.refresh_from_db()

        response_data.update({
            'total_sum': float(baskets.total_sum()),
            'total_quantity': baskets.total_quantity(),
            'product_sum': float(basket.sum()),
            'quantity': basket.quantity,
        })

        return JsonResponse(response_data)
    else:
        return JsonResponse({
            'success': False,
            'message': translate_text_to_user_language('Invalid request', request)
            })


def product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    prev_page = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else '/'

    context = {
        'title': product.name,
        'product': product,
        'previous_page': prev_page,
    }

    return render(request, 'products/product-view.html', context)