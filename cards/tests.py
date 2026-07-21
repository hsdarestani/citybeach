from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import RegistrationForm
from .models import Business, CustomerProfile, Venue, Wallet


class GermanInterfaceTests(TestCase):
    def test_login_page_is_german_and_contains_apple_button(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mit Apple fortfahren')
        self.assertContains(response, 'Anmelden')
        self.assertNotContains(response, 'WELCOME BACK')
        self.assertNotContains(response, 'Your rooftop is waiting')

    def test_landing_page_uses_german_titles(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DEIN SOMMER')
        self.assertContains(response, 'Angebote &amp; Veranstaltungen')
        self.assertNotContains(response, 'CHOOSE YOUR VIBE')
        self.assertNotContains(response, 'OFFERS &amp; EVENTS')


class RegistrationAgeTests(TestCase):
    def test_underage_registration_is_rejected(self):
        today = date.today()
        form = RegistrationForm(data={
            'first_name': 'Junger',
            'last_name': 'Gast',
            'email': 'jung@example.com',
            'phone': '+49 170 1111111',
            'birth_date': date(today.year - 17, today.month, today.day),
            'age_confirmed': True,
            'password1': 'EinSicheresPasswort!2026',
            'password2': 'EinSicheresPasswort!2026',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)


class AppleProfileCompletionTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(name='CityBeach Frankfurt', slug='citybeach-frankfurt')
        self.venue = Venue.objects.create(business=self.business, name='CityBeach Frankfurt', slug='citybeach')
        self.user = get_user_model().objects.create_user(
            username='apple@example.com',
            email='apple@example.com',
            password='EinSicheresPasswort!2026',
            first_name='Apple',
            last_name='Gast',
        )
        CustomerProfile.objects.create(user=self.user, email_verified=True, selected_venue=self.venue)
        Wallet.objects.create(
            business=self.business,
            owner=self.user,
            display_name='Apple Gast',
            email=self.user.email,
        )
        self.client.force_login(self.user)

    def test_incomplete_apple_profile_redirects_to_completion(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('complete_customer_profile'), fetch_redirect_response=False)

    def test_profile_can_be_completed(self):
        response = self.client.post(reverse('complete_customer_profile'), {
            'phone': '+49 170 2222222',
            'birth_date': '1990-01-01',
            'age_confirmed': True,
        })
        self.assertRedirects(response, reverse('customer_dashboard'), fetch_redirect_response=False)
        profile = CustomerProfile.objects.get(user=self.user)
        wallet = Wallet.objects.get(owner=self.user)
        self.assertEqual(profile.phone, '+49 170 2222222')
        self.assertEqual(wallet.phone, '+49 170 2222222')
