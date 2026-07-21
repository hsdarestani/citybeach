from pathlib import Path
import base64
import os

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-secret')
DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = [x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if x.strip()]
CSRF_TRUSTED_ORIGINS = [x.strip() for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if x.strip()]

# Apple-Anmeldung. Die neuen Variablennamen entsprechen den GitHub-Geheimnissen.
# Die bisherigen Namen bleiben als Rückwärtskompatibilität erhalten.
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID', os.getenv('APPLE_SERVICE_ID', '')).strip()
APPLE_BUNDLE_ID = os.getenv('APPLE_BUNDLE_ID', '').strip()
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID', '').strip()
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID', '').strip()
APPLE_REDIRECT_URI = os.getenv(
    'APPLE_REDIRECT_URI',
    'https://citybeach.smarbiz.sbs/accounts/apple/callback/',
).strip()
APPLE_PRIVATE_KEY_VALUE = os.getenv(
    'APPLE_PRIVATE_KEY_BASE64',
    os.getenv('APPLE_PRIVATE_KEY_B64', ''),
).strip()


def _decode_apple_private_key(value):
    """Akzeptiert sowohl den rohen .p8-Inhalt als auch Base64."""
    if not value:
        return ''
    normalized = value.replace('\\n', '\n').strip()
    if '-----BEGIN PRIVATE KEY-----' in normalized:
        return normalized
    try:
        decoded = base64.b64decode(''.join(normalized.split()), validate=True).decode('utf-8').strip()
    except (ValueError, UnicodeDecodeError):
        return ''
    return decoded if '-----BEGIN PRIVATE KEY-----' in decoded else ''


APPLE_PRIVATE_KEY = _decode_apple_private_key(APPLE_PRIVATE_KEY_VALUE)
APPLE_LOGIN_ENABLED = all([
    APPLE_CLIENT_ID,
    APPLE_KEY_ID,
    APPLE_TEAM_ID,
    APPLE_PRIVATE_KEY,
    APPLE_REDIRECT_URI,
])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.apple',
    'rest_framework',
    'cards',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'cards.context_processors.brand_context',
        ]
    },
}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600)}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'cards.adapters.CityBeachSocialAccountAdapter'

# Die konkrete Apple-Anwendung wird durch `seed_demo` als SocialApp in der
# Datenbank angelegt und mit SITE_ID=1 verbunden. Dadurch verwendet allauth
# genau eine eindeutige Konfiguration und es entstehen keine doppelten Apps.
SOCIALACCOUNT_PROVIDERS = {'apple': {}}

SESSION_COOKIE_SECURE = os.getenv('DJANGO_SECURE_COOKIES', '0') == '1'
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SESSION_COOKIE_SAMESITE = 'None' if APPLE_LOGIN_ENABLED else 'Lax'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_HSTS_SECONDS', '0'))
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = 'CityBeach Frankfurt <app@citybeach-frankfurt.de>'
