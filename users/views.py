from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.settings import LOGIN_URL
from users.utils import translate_text_to_user_language
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from products.models import Basket
from payments.models import ExchangeRate


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST, request=request)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm(request=request)
    context = {
        'title': translate_text_to_user_language('Authorization', request),
        'form': form,
    }
    return render(request, 'users/login.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, translate_text_to_user_language('You have successfully registered!', request))
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserRegistrationForm(request=request)

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

    for basket in baskets:
        basket.currency, basket.price = ExchangeRate.get_user_currency_and_converted_product_price(request, basket.product)
        basket.save()

    context = {
        'title': translate_text_to_user_language('Profile', request),
        'form': form,
        'baskets': baskets,
    }

    return render(request, 'users/profile.html', context)


@login_required(login_url=LOGIN_URL)
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
