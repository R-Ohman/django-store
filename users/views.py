from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.settings import LOGIN_URL
from store.translator import translate_text_to_user_language
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, OrderForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from products.models import Basket
from products.models import OrderItem
from users.models import Order


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm()
    context = {
        'title': translate_text_to_user_language('Authorization', request),
        'form': form,
    }
    return render(request, 'users/login.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, translate_text_to_user_language('You have successfully registered!', request))
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserRegistrationForm()

    context = {
        'title': translate_text_to_user_language('Registration', request),
        'form': form,
        'errors': [error for field, error in form.errors.items()],
    }
    return render(request, 'users/registration.html', context)


@login_required(login_url=LOGIN_URL)
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(instance=request.user, files=request.FILES, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, translate_text_to_user_language('The data has been successfully changed!', request))
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = UserProfileForm(instance=request.user)

    baskets = Basket.objects.filter(user=request.user)
    context = {
        'title': translate_text_to_user_language('Profile', request),
        'form': form,
        'baskets': baskets,
        'total_sum': baskets.total_sum(),
        'total_quantity': baskets.total_quantity(),
    }
    for basket in baskets:
        print(basket.quantity)

    return render(request, 'users/profile.html', context)


@login_required(login_url=LOGIN_URL)
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required(login_url=LOGIN_URL)
def place_order(request):
    baskets = Basket.objects.filter(user=request.user)
    form = OrderForm()
    errors = []

    if request.method == 'POST':
        form = OrderForm(data=request.POST)
        if form.is_valid():
            for basket in baskets:
                if basket.product.quantity < basket.quantity:
                    errors.append(translate_text_to_user_language('There are not enough items in stock.', request))
                    break

            if not baskets or not form.is_valid():
                errors.append(translate_text_to_user_language('Error during order execution.', request))
            else:
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                for basket in baskets:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=basket.product,
                        quantity=basket.quantity,
                        user=basket.user,
                    )
                    basket.product.quantity -= basket.quantity
                    basket.product.save()

                baskets.delete()

                return HttpResponseRedirect(reverse('user:orders_history'))


    context = {
        'title': translate_text_to_user_language('Order placement', request),
        'baskets': baskets,
        'total_sum': baskets.total_sum(),
        'total_quantity': baskets.total_quantity(),
        'errors': errors,
        'form': form,
    }

    for field, error in form.errors.items():
        context['errors'].append(error)

    return render(request, 'users/order-create.html', context)



def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')

    context = {
        'title': translate_text_to_user_language('Order history', request),
        'orders': orders,
    }
    return render(request, 'users/orders.html', context)

def order_view(request, pk):
    order = Order.objects.get(id=pk)
    context = {
        'title': translate_text_to_user_language(f'Order №{order.id}', request),
        'order': order,
        'product_baskets': OrderItem.objects.filter(order=order),
    }
    return render(request, 'users/order-view.html', context)