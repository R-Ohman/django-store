from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from store.settings import LOGIN_URL
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from products.models import Basket


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
        'title': 'Авторизация',
        'form': form,
    }
    return render(request, 'users/login.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались!')
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserRegistrationForm()


    context = {
        'title': 'Регистрация',
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
            messages.success(request, 'Данные успешно изменены!')
            return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = UserProfileForm(instance=request.user)

    baskets = Basket.objects.filter(user=request.user)
    context = {
        'title': 'Профиль',
        'form': form,
        'baskets': baskets,
        'total_sum': baskets.total_sum(),
        'total_quantity': baskets.total_quantity(),
    }
    return render(request, 'users/profile.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))