from django.conf import settings
from django.http import HttpRequest

from allauth.socialaccount.providers.apple.views import (
    AppleOAuth2Adapter,
    apple_post_callback,
)
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)


class CityBeachAppleOAuth2Adapter(AppleOAuth2Adapter):
    """Verwendet exakt die bei Apple registrierte Rücksprungadresse."""

    def get_callback_url(self, request: HttpRequest, app):
        return settings.APPLE_REDIRECT_URI


apple_login = OAuth2LoginView.adapter_view(CityBeachAppleOAuth2Adapter)
apple_finish_login = OAuth2CallbackView.adapter_view(CityBeachAppleOAuth2Adapter)


def apple_callback(request: HttpRequest):
    return apple_post_callback(
        request,
        finish_endpoint_name="citybeach_apple_finish_callback",
    )
