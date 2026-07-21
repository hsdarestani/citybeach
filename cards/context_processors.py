from django.conf import settings


def brand_context(request):
    return {
        'brand_name': 'CityBeach Frankfurt',
        'brand_tagline': 'Sommer über den Dächern der Stadt',
        'powered_by': 'Technik von A+',
        'apple_login_enabled': settings.APPLE_LOGIN_ENABLED,
    }
