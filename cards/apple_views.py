from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.providers.apple.views import (
    AppleOAuth2Adapter,
    apple_post_callback,
)
from allauth.socialaccount.providers.base.utils import respond_to_login_on_get
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView


class CityBeachAppleOAuth2Adapter(AppleOAuth2Adapter):
    """Verwendet exakt die bei Apple registrierte Rücksprungadresse."""

    def get_callback_url(self, request: HttpRequest, app):
        return settings.APPLE_REDIRECT_URI


@login_not_required
def apple_login(request: HttpRequest):
    """Startet Apple OAuth mit dem CityBeach-Adapter auch auf Provider-Ebene.

    django-allauth erstellt den eigentlichen Autorisierungs-Link über den
    Provider. Ohne diese Zuweisung würde der Provider erneut den Standard-
    Adapter verwenden und `/accounts/apple/login/callback/` erzeugen.
    """
    adapter = CityBeachAppleOAuth2Adapter(request)
    provider = adapter.get_provider()
    provider.oauth2_adapter_class = CityBeachAppleOAuth2Adapter

    response = respond_to_login_on_get(request, provider)
    if response:
        return response
    return provider.redirect_from_request(request)


apple_finish_login = OAuth2CallbackView.adapter_view(CityBeachAppleOAuth2Adapter)


@csrf_exempt
@login_not_required
def apple_callback(request: HttpRequest):
    return apple_post_callback(
        request,
        finish_endpoint_name="citybeach_apple_finish_callback",
    )
