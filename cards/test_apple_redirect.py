from urllib.parse import parse_qs, urlparse

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings


APPLE_CALLBACK = 'https://citybeach.smarbiz.sbs/accounts/apple/callback/'


@override_settings(
    APPLE_REDIRECT_URI=APPLE_CALLBACK,
    SOCIALACCOUNT_LOGIN_ON_GET=True,
)
class AppleAuthorizationRedirectTests(TestCase):
    def setUp(self):
        site, _ = Site.objects.update_or_create(
            pk=1,
            defaults={
                'domain': 'citybeach.smarbiz.sbs',
                'name': 'CityBeach Frankfurt',
            },
        )
        app = SocialApp.objects.create(
            provider='apple',
            name='CityBeach Apple',
            client_id='sbs.smarbiz.citybeach.web',
            secret='TESTKEY123',
            key='TESTTEAM123',
            settings={'certificate_key': '-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----'},
        )
        app.sites.add(site)

    def test_authorization_url_uses_registered_citybeach_callback(self):
        response = self.client.get(
            '/accounts/apple/login/',
            secure=True,
            HTTP_HOST='citybeach.smarbiz.sbs',
        )
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlparse(response.headers['Location']).query)
        self.assertEqual(query['redirect_uri'][0], APPLE_CALLBACK)
        self.assertNotIn('/accounts/apple/login/callback/', query['redirect_uri'][0])
