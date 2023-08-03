import json
from urllib.parse import urlparse

from django.contrib import messages
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse

from products.models import ProductCategory, Product, Basket, CarouselImage, Carousel, ProductFollower
from payments.models import ExchangeRate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from products.utils import round_number
from store.settings import LOGIN_URL
from users.translator import translate_text_to_user_language


def index(request):

    context = {
        'is_promotion': False,
    }
    return render(request, 'products/index.html', context)


def filter_products(request, category_id=None, category_products=None):
    if category_products:
        # filtered_products = Product.objects.filter(is_visible=True).order_by('price')
        lowest_price_product = min(category_products, key=lambda product: product.discounted_price)
        highest_price_product = max(category_products, key=lambda product: product.discounted_price)

        lowest_price = ExchangeRate.convert_to_user_currency(request, lowest_price_product.price)
        highest_price = ExchangeRate.convert_to_user_currency(request, highest_price_product.price)
        lowest_price = int(lowest_price_product.discount_multiply(lowest_price))
        highest_price = int(highest_price_product.discount_multiply(highest_price))

        # get min and max price from user
        min_price, max_price = request.GET.get('price').split('-') if request.GET.get('price') else (None, None)
        min_price = int(min_price) if min_price else None
        max_price = int(max_price) if max_price else None

        if not min_price or not lowest_price <= min_price <= highest_price:
            min_price = lowest_price
        if not max_price or not lowest_price <= max_price <= highest_price:
            max_price = highest_price

        if min_price > max_price:
            min_price, max_price = max_price, min_price

        min_price_base = ExchangeRate.convert_from_user_to_base(request, min_price)
        max_price_base = ExchangeRate.convert_from_user_to_base(request, max_price)
        products = list(filter(lambda product: min_price_base <= product.discounted_price <= max_price_base, category_products))

        currency, products_with_converted_price = None, []
        for product in products:
            currency, converted_price = ExchangeRate.get_user_currency_and_converted_product_price(request, product)
            products_with_converted_price.append({
                'product': product,
                'price': round_number(converted_price),
                'discounted_price': round_number(product.discount_multiply(converted_price)),
            })

        return {
            'category_products': category_products,
            'products_with_converted_price': products_with_converted_price,
            'lowest_price': str(lowest_price),
            'highest_price': str(highest_price),
            'min_price': str(min_price),
            'max_price': str(max_price),
            'category': ProductCategory.objects.get(id=category_id) if category_id else None,
            'currency': currency,
        }
    return {
        'products_with_converted_price': [],
        'min_price': None,
        'max_price': None,
        'currency': None,
        'category': ProductCategory.objects.get(id=category_id) if category_id else None,
    }


def products(request, category_id=None):
    sort_by = request.COOKIES.get('sort_by') if request.COOKIES.get('sort_by') else "none"

    ordered_products = Product.objects.filter(is_visible=True)

    if request.GET.get('cat'):
        category_id = int(request.GET.get('cat'))
        ordered_products = ordered_products.filter(category_id=category_id)

    search_text = request.GET.get('search') if request.GET.get('search') else None
    if search_text:
        ordered_products = ordered_products.filter(
            Q(name__icontains=search_text)
        )


    if sort_by in ['asc', 'desc']:
        ordered_products = sorted(ordered_products, key=lambda product: product.discounted_price)
        if sort_by == 'desc':
            ordered_products = ordered_products[::-1]

    elif sort_by == 'top':
        ordered_products = sorted(ordered_products, key=lambda product: product.assessment, reverse=True)
    elif sort_by == 'pop':
        ordered_products = sorted(ordered_products, key=lambda product: product.comments.count(), reverse=True)

    products = []
    for product in ordered_products:
        if product.quantity > 0:
            products.append(product)
    for product in ordered_products:
        if product.quantity == 0:
            products.append(product)

    context = filter_products(request, category_products=products, category_id=category_id)
    page = request.GET.get('page', 1)
    per_page = int(request.COOKIES.get('per_page', 3))
    paginator = Paginator(context['products_with_converted_price'], per_page)

    try:
        page_number = int(page)
        page_products = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_products = paginator.page(1)

    if request.is_ajax():
        context = {
            'products_with_converted_price': page_products,
            'currency': context['currency'],
            'current_page': int(page),
            'sort_by': sort_by,
            'search_text': search_text,
        }
        product_list_html = render_to_string('products/product_cards.html', context)
        page_list_html = render_to_string('products/pagination.html', context)
        return JsonResponse({
            'product_list_html': product_list_html,
            'page_list_html': page_list_html
            })

    context.update(
        {
            'sort_by': sort_by,
            'products_with_converted_price': page_products,
            'categories': ProductCategory.objects.all(),
            'current_page': int(page),
            'carousel_images': CarouselImage.objects.filter(carousel=Carousel.objects.get(name="products_main_page")),
            'search_text': search_text,
        }
    )
    return render(request, 'products/products.html', context)


@login_required(login_url=LOGIN_URL)
def add_to_basket(request, product_id):
    product = Product.objects.get(id=product_id)
    basket = Basket.objects.filter(user=request.user, product=product).first()

    message = product.name + translate_text_to_user_language(' has been successfully added to your cart', request)
    success = True

    if basket and basket.quantity < basket.product.quantity:
        basket.quantity += 1
        basket.save()
    elif not basket and product.quantity > 0:
        Basket.objects.create(user=request.user, product_id=product_id, quantity=1)
    else:
        message = translate_text_to_user_language('Not enough goods in stock =(', request)
        success = False

    response = {
        'success': success,
        'message': message,
    }

    if urlparse(request.META.get('HTTP_REFERER')).path == reverse('user:profile'):
        baskets = Basket.objects.filter(user=request.user)
        for basket in baskets:
            basket.currency, basket.price = ExchangeRate.get_user_currency_and_converted_product_price(request, basket.product)
            basket.save()
        basket_html = render_to_string('products/basket.html', {'baskets': baskets})
        response.update({'basket_list_html': basket_html})

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


def product_discount_expiration(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        time_to_expiration = product.time_to_discount_expiration
        return JsonResponse({'time_to_expiration': time_to_expiration})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@login_required(login_url=LOGIN_URL)
def follow_product_availability(request, product_id):
    product = Product.objects.get(id=product_id)
    follower = ProductFollower.objects.filter(user=request.user, product=product)
    if follower.exists():
        follower = follower.first()
        message = translate_text_to_user_language('You are already following this product', request)
        success = False
    else:
        follower = ProductFollower.objects.create(user=request.user, product=product)
        message = translate_text_to_user_language('You are now following this product', request)
        success = True

    response = {
        'success': success,
        'message': message,
        'product': product.name}

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        following_products_html = render_to_string('users/following_products.html', {'user': request.user })
        response.update({'following_products_html': following_products_html})

    return JsonResponse(response)


@login_required(login_url=LOGIN_URL)
def unfollow_product(request, product_id):
    product = Product.objects.get(id=product_id)
    follower = ProductFollower.objects.filter(user=request.user, product=product)
    if follower.exists():
        follower = follower.first()
        follower.delete()
        success = True
        message = translate_text_to_user_language('You are no longer following this product', request)
    else:
        success = False
        message = translate_text_to_user_language('You are not following this product', request)

    return JsonResponse({
        'success': success,
        'message': message,
    })