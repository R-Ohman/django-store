from django.shortcuts import render
from users.forms import UserLoginForm, UserRegistrationForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth


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
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserRegistrationForm()

    context = {
        'title': 'Регистрация',
        'form': form,
        }
    return render(request, 'users/registration.html', context)


def profile(request):
    return render(request, 'users/profile.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))