from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Business, CustomerProfile, Wallet


class CityBeachSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Erstellt bei der ersten Apple-Anmeldung automatisch das Kundenkonto."""

    def is_auto_signup_allowed(self, request, sociallogin):
        return bool(sociallogin.user.email)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        business = Business.objects.first()
        if business is None:
            return user

        profile, _ = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                'email_verified': True,
                'selected_venue': business.venues.filter(is_active=True).first(),
            },
        )
        if not profile.email_verified:
            profile.email_verified = True
            profile.save(update_fields=['email_verified'])

        display_name = user.get_full_name().strip() or user.email or 'CityBeach-Mitglied'
        Wallet.objects.get_or_create(
            owner=user,
            defaults={
                'business': business,
                'display_name': display_name,
                'email': user.email,
            },
        )
        return user
