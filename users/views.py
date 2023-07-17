from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from store.settings import LOGIN_URL
from users.utils import translate_text_to_user_language
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from products.models import Basket
from payments.models import ExchangeRate


def login(request):
    errors = request.GET.getlist('errors', [])

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
        'errors': errors,
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


def signup_redirect(request):
    return redirect(reverse('user:login'))


# views.py

from django.shortcuts import redirect
from social_django.utils import psa

def google_oauth2_login(request):
    return _oauth2_login(request, backend='google-oauth2')


@psa('social:complete')
def _oauth2_login(request, backend):
    try:
        # В этой промежуточной функции `request.backend` будет содержать данные о провайдере (в данном случае, Google OAuth2)

        # Если аутентификация была успешной, `request.user` будет содержать пользователя, или None, если неудача
        if request.user is not None and request.user.is_authenticated:
            # Выполните перенаправление на нужную страницу после успешной аутентификации
            return redirect('/')  # Замените '/' на URL-шаблон для главной страницы

        # Если аутентификация не удалась или пользователь не аутентифицирован, перенаправьте на страницу входа с ошибкой
        errors = ['Authentication failed. Please try again.']
        redirect_url = reverse('user:login') + '?errors=' + '&errors='.join(errors)
        return redirect(redirect_url)
    except Exception as e:
        # Выводим более подробную информацию об ошибке в консоли, чтобы легче отследить проблему
        print("Error during Google OAuth2 login:", e)
        raise e
