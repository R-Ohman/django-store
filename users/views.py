from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from store.settings import LOGIN_URL
from users.models import User
from users.utils import translate_text_to_user_language, check_referer_no_keywords
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserResetPasswordForm, \
    UserResetPasswordEmailForm
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from products.models import Basket
from payments.models import ExchangeRate

# Email
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login

from users.tokens import account_activation_token


@login_required(login_url=LOGIN_URL)
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_confirmed = True
        user.save()
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, translate_text_to_user_language(f'Dear, {user.first_name}, your account is \
                                successfully activated.', request))
        return redirect(reverse('user:profile'))
    else:
        messages.error(request, translate_text_to_user_language('Activation link is invalid!', request))
        return redirect(reverse('index'))


@login_required(login_url=LOGIN_URL)
def activate_email(request, user, to_email):
    mail_subject = translate_text_to_user_language('Activate your account.', request)
    message = render_to_string('users/email_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, translate_text_to_user_language(f'Please go to your \
                                email {to_email} inbox and click on received activation link to confirm \
                                and complete the registration. Note: Check your spam folder.', request))
    else:
        messages.error(request, translate_text_to_user_language('Sorry, we could not send you an activation link. \
                                Please try again later.', request))


def login(request):
    if request.user.is_authenticated:
        messages.error(request, translate_text_to_user_language('You are already logged in!', request))
        return redirect(reverse('user:profile'))

    next_url = '/'
    errors = request.GET.getlist('errors', [])
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST, request=request)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                next_url = request.POST.get('next', '/')
                return redirect(next_url)
    else:
        if request.GET.get('next'):
            next_url = request.GET.get('next')
        elif request.META.get('HTTP_REFERER') and check_referer_no_keywords(request):
            print(request.META.get('HTTP_REFERER'))
            next_url = request.META.get('HTTP_REFERER')
        form = UserLoginForm(request=request)

    context = {
        'title': translate_text_to_user_language('Authorization', request),
        'form': form,
        'errors': errors,
        'next': next_url,
    }
    return render(request, 'users/login.html', context)


def registration(request):
    if request.user.is_authenticated:
        messages.error(request, translate_text_to_user_language('You are already logged in!', request))
        return redirect(reverse('user:profile'))

    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.save()
            activate_email(request, user, form.cleaned_data.get('email'))

            messages.success(request, translate_text_to_user_language('You have been successfully registered!', request))
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
        form = UserProfileForm(instance=request.user, files=request.FILES, data=request.POST, request=request)
        if form.is_valid():
            if form.cleaned_data.get('username') != request.user.username and request.user.number_of_available_username_changes == 0:
                messages.error(request, translate_text_to_user_language('You cannot change your username!', request))
                return HttpResponseRedirect(reverse('user:profile'))
            elif form.cleaned_data.get('username') != request.user.username and request.user.number_of_available_username_changes > 0:
                request.user.number_of_available_username_changes -= 1
                request.user.save()

            user = form.save()
            if form.cleaned_data.get('email') and not user.is_confirmed:
                activate_email(request, user, form.cleaned_data.get('email'))

            messages.success(request, translate_text_to_user_language('The data has been successfully changed!', request))
        else:
            print(form.errors)
            messages.error(request, translate_text_to_user_language('Something went wrong, maybe this username or email \
                                    is already in use!', request))
        return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = UserProfileForm(instance=request.user, request=request)

    baskets = Basket.objects.filter(user=request.user)

    for basket in baskets:
        basket.currency, basket.price = ExchangeRate.get_user_currency_and_converted_product_price(request, basket.product)
        basket.save()

    context = {
        'title': translate_text_to_user_language('Profile', request),
        'form': form,
        'baskets': baskets,
        'user': request.user,
    }

    return render(request, 'users/profile.html', context)


@login_required(login_url=LOGIN_URL)
def logout(request):
    auth.logout(request)
    messages.success(request, translate_text_to_user_language('You have successfully logged out!', request))
    return HttpResponseRedirect(reverse('index'))


def signup_redirect(request):
    messages.error(request, translate_text_to_user_language('Something went wrong, it may be that the user with this email already exists!', request))
    return redirect(reverse('user:login'))


def reset(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not account_activation_token.check_token(user, token):
            messages.error(request, translate_text_to_user_language('Sorry, the link is no longer valid!', request))
            return redirect(reverse('user:reset_password'))
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == 'POST':
        form = UserResetPasswordForm(data=request.POST, request=request)
        if form.is_valid():
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            messages.success(request, translate_text_to_user_language('Your password has been successfully changed!', request))
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = UserResetPasswordForm(request=request)

    context = {
        'title': translate_text_to_user_language('Reset password', request),
        'form': form,
        'uidb64': uidb64,
        'token': token,
        'errors': [error for field, error in form.errors.items()],
    }
    return render(request, 'users/reset_password.html', context)


def reset_email(request, user):
    current_site = get_current_site(request)
    subject = translate_text_to_user_language('Reset password', request)
    message = render_to_string('users/email_reset_password.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'title': translate_text_to_user_language('Reset password', request),
    })
    user.email_user(subject, message)


def reset_password(request):
    if request.user.is_authenticated:
        messages.error(request, translate_text_to_user_language('You are already logged in!', request))
        return redirect(reverse('user:profile'))

    if request.method == 'POST':
        form = UserResetPasswordEmailForm(data=request.POST, request=request)
        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data.get('email')).first()

            context = {
                'title': translate_text_to_user_language('Reset password', request),
                'form': form,
            }

            if user:
                reset_email(request, user)
                context['email'] = form.cleaned_data.get('email')
                messages.add_message(request, messages.SUCCESS, translate_text_to_user_language(
                    'An email has been sent to your email address with a link to reset your password!', request))
            else:
                messages.add_message(request, messages.ERROR,
                                     translate_text_to_user_language('User with this email does not exist!', request))

            return render(request, 'users/reset_password_email_form.html', context)
    else:
        form = UserResetPasswordEmailForm(request=request)

    context = {
        'title': translate_text_to_user_language('Reset password', request),
        'form': form,
    }
    return render(request, 'users/reset_password_email_form.html', context)
