from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve as media_serve

from cards import apple_views
from cards.views import manifest_view, service_worker_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/apple/login/', apple_views.apple_login, name='apple_login'),
    path('accounts/apple/callback/', apple_views.apple_callback, name='apple_callback'),
    path(
        'accounts/apple/callback/finish/',
        apple_views.apple_finish_login,
        name='citybeach_apple_finish_callback',
    ),
    path('accounts/', include('allauth.urls')),
    path('manifest.webmanifest', manifest_view, name='manifest'),
    path('service-worker.js', service_worker_view, name='service_worker'),
    path('', include('cards.urls')),
    re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': settings.MEDIA_ROOT}),
]
