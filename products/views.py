import json

from django.contrib import messages
from decimal import Decimal

from django.db.models import F
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse

from products.models import ProductCategory, Product, Basket, CarouselImage, Carousel
from payments.models import ExchangeRate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from products.utils import round_number, number_to_float
from store.settings import LOGIN_URL
from users.translator import translate_text_to_user_language


def index(request):

    context = {
        'is_promotion': False,
    }
    return render(request, 'products/index.html', context)


def products(request, category_id=None):
    all_products = Product.objects.filter(category_id=category_id, is_visible=True) if category_id else Product.objects.filter(is_visible=True)
    products = all_products.order_by('-id')

    min_price, max_price = request.GET.get('price').split('-') if request.GET.get('price') else (None, None)
    if min_price and max_price:
        min_price = ExchangeRate.convert_from_user_to_base(request, int(min_price))
        max_price = ExchangeRate.convert_from_user_to_base(request, int(max_price))

        products = list(filter(lambda product: min_price <= product.discounted_price <= max_price, products))


    currency = None
    products_with_converted_price = []
    for product in products:
        currency, converted_price = ExchangeRate.get_user_currency_and_converted_product_price(request, product)
        products_with_converted_price.append({
            'product': product,
            'price': round_number(converted_price),
            'discounted_price': round_number(product.discount_multiply(converted_price)),
        })
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
            'currency': currency,
            'current_page': int(page),
        }
        product_list_html = render_to_string('products/product_cards.html', context)
        page_list_html = render_to_string('products/pagination.html', context)
        return JsonResponse({
            'product_list_html': product_list_html,
            'page_list_html': page_list_html
            })

    #filtered_products = Product.objects.filter(is_visible=True).order_by('price')
    lowest_price_product = min(all_products, key=lambda product: product.discounted_price)
    highest_price_product = max(all_products, key=lambda product: product.discounted_price)
    lowest_price = ExchangeRate.convert_to_user_currency(request, lowest_price_product.price)
    highest_price = ExchangeRate.convert_to_user_currency(request, highest_price_product.price)
    lowest_price = int(lowest_price_product.discount_multiply(lowest_price))
    highest_price = int(highest_price_product.discount_multiply(highest_price))

    min_price, max_price = request.GET.get('price').split('-') if request.GET.get('price') else (None, None)

    context = {
        'products_with_converted_price': page_products,
        'categories': ProductCategory.objects.all(),
        'current_page': int(page),  # Добавляем текущую страницу в контекст
        'category': ProductCategory.objects.get(id=category_id) if category_id else None,
        'currency': currency,
        'carousel_images': CarouselImage.objects.filter(carousel=Carousel.objects.get(name="products_main_page")),

        'lowest_price': lowest_price,
        'highest_price': highest_price,
        'min_price': min_price if min_price else lowest_price,
        'max_price': max_price if max_price else highest_price,
    }

    return render(request, 'products/products.html', context)


@login_required(login_url=LOGIN_URL)
def add_product(request, product_id):
    basket = Basket.objects.filter(user=request.user, product_id=product_id).first()

    response = {
        'success': True,
        'product_name': Product.objects.get(id=product_id).name,
        'message': translate_text_to_user_language('has been successfully added to your cart', request),
    }

    if basket and basket.quantity < basket.product.quantity:
        basket.quantity += 1
        basket.save()
    elif not basket and Product.objects.get(id=product_id).quantity > 0:
        Basket.objects.create(user=request.user, product_id=product_id, quantity=1)
    else:
        response = {
            'success': False,
            'message': translate_text_to_user_language('Not enough goods in stock =(', request),
        }

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
            'total_sum': baskets.total_sum(),
            'total_quantity': baskets.total_quantity(),
            'product_sum': basket.sum,
            'product_sum_without_discount': basket.sum_without_discount,
            'quantity': basket.quantity,
        })

        return JsonResponse(response_data)
    else:
        return JsonResponse({
            'success': False,
            'message': translate_text_to_user_language('Invalid request', request)
            })

@login_required
def empty_cart(request):
    user_baskets = Basket.objects.filter(user=request.user)
    if user_baskets:
        for basket in user_baskets:
            basket.delete()

        messages.success(request, translate_text_to_user_language('Cart has been successfully emptied', request))
    else:
        messages.error(request, translate_text_to_user_language('Your cart is already empty!', request))

    return redirect(request.META.get('HTTP_REFERER', reverse('user:profile')))
