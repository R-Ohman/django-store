from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

from products.views import index
from users.views import signup_redirect

urlpatterns = [
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
