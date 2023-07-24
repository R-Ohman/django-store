from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.views.generic import RedirectView

from products.views import index
from store.settings import STATIC_URL
from users.views import signup_redirect

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url = STATIC_URL + 'vendor/img/store/favicon.ico')),
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('products/', include('products.urls', namespace='products')),
    path('user/', include('users.urls', namespace='user')),
    path('i18n/', include('django.conf.urls.i18n')),

    path('social/signup/', signup_redirect, name='signup_redirect'),
    path('', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
