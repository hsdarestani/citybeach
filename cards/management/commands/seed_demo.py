import os
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from cards.models import Business, BusinessSettings, CustomerProfile, LedgerEntry, Membership, Offer, Venue, Wallet
from cards.services import post_entry


class Command(BaseCommand):
    help = 'Erstellt die CityBeach-Demodaten wiederholbar und ohne Duplikate.'

    def handle(self, *args, **options):
        User = get_user_model()
        Site.objects.update_or_create(
            pk=1,
            defaults={'domain': 'citybeach.smarbiz.sbs', 'name': 'CityBeach Frankfurt'},
        )
        business, _ = Business.objects.update_or_create(
            slug='citybeach-frankfurt',
            defaults={'name': 'CityBeach Frankfurt', 'currency': 'EUR'},
        )
        BusinessSettings.objects.get_or_create(business=business)
        beach, _ = Venue.objects.update_or_create(
            business=business,
            slug='citybeach',
            defaults={
                'name': 'CityBeach Frankfurt',
                'theme': Venue.Theme.BEACH,
                'subtitle': 'Sommer über den Dächern Frankfurts',
                'address': 'Carl-Theodor-Reiffenstein-Platz 5, 60313 Frankfurt am Main · Zugang über Töngesgasse 8',
                'opening_hours': 'So–Mi 12–22 Uhr · Do–Sa 12–00 Uhr · nur bei gutem Wetter',
                'website_url': 'https://www.citybeach-frankfurt.de/',
                'instagram_url': 'https://www.instagram.com/citybeachfrankfurt/',
                'reservation_url': 'https://www.citybeach-frankfurt.de/',
                'position': 1,
                'is_active': True,
            },
        )
        Venue.objects.update_or_create(
            business=business,
            slug='cityalm',
            defaults={
                'name': 'CityAlm Frankfurt',
                'theme': Venue.Theme.ALM,
                'subtitle': 'Winterzauber über den Dächern Frankfurts',
                'address': 'Carl-Theodor-Reiffenstein-Platz 5, 60313 Frankfurt am Main',
                'website_url': 'https://www.cityalm.de/',
                'instagram_url': 'https://www.instagram.com/citybeachfrankfurt/',
                'position': 2,
                'is_active': True,
            },
        )

        owner_password = os.getenv('CITYBEACH_OWNER_PASSWORD', 'CityBeachInhaber!2026')
        staff_password = os.getenv('CITYBEACH_STAFF_PASSWORD', 'CityBeachMitarbeiter!2026')
        customer_password = os.getenv('CITYBEACH_CUSTOMER_PASSWORD', 'CityBeachGast!2026')

        owner, _ = User.objects.get_or_create(username='owner')
        owner.email = 'inhaber@citybeach.local'
        owner.first_name = 'CityBeach'
        owner.last_name = 'Inhaber'
        owner.set_password(owner_password)
        owner.is_staff = True
        owner.is_superuser = True
        owner.save()

        staff, _ = User.objects.get_or_create(username='staff')
        staff.email = 'mitarbeiter@citybeach.local'
        staff.first_name = 'CityBeach'
        staff.last_name = 'Mitarbeiter'
        staff.set_password(staff_password)
        staff.save()

        customer, _ = User.objects.get_or_create(username='customer')
        customer.email = 'gast@citybeach.local'
        customer.first_name = 'Sonniger'
        customer.last_name = 'Gast'
        customer.set_password(customer_password)
        customer.save()

        Membership.objects.update_or_create(
            user=owner,
            business=business,
            defaults={'role': Membership.Role.OWNER, 'is_active': True, 'can_manage_content': True},
        )
        Membership.objects.update_or_create(
            user=staff,
            business=business,
            defaults={'role': Membership.Role.STAFF, 'is_active': True},
        )
        CustomerProfile.objects.update_or_create(
            user=customer,
            defaults={
                'phone': '+49 170 0000000',
                'birth_date': date(1990, 1, 1),
                'selected_venue': beach,
                'email_verified': True,
            },
        )
        wallet, _ = Wallet.objects.get_or_create(
            owner=customer,
            defaults={
                'business': business,
                'display_name': 'Sonniger Gast',
                'email': customer.email,
                'phone': '+49 170 0000000',
            },
        )
        wallet.display_name = 'Sonniger Gast'
        wallet.email = customer.email
        wallet.phone = '+49 170 0000000'
        wallet.save(update_fields=['display_name', 'email', 'phone', 'updated_at'])

        LedgerEntry.objects.filter(description='Welcome Guthaben').update(description='Startguthaben')
        LedgerEntry.objects.filter(description='10% Welcome Bonus').update(description='10 % Willkommensbonus')
        if wallet.balance == 0:
            post_entry(wallet=wallet, venue=beach, entry_type=LedgerEntry.Type.TOPUP, amount=Decimal('200'), actor=owner, description='Startguthaben')
            post_entry(wallet=wallet, venue=beach, entry_type=LedgerEntry.Type.BONUS, amount=Decimal('20'), actor=owner, description='10 % Willkommensbonus')

        old_offer = Offer.objects.filter(business=business, title='Sunset Welcome').first()
        if old_offer:
            old_offer.title = 'Willkommen zum Sonnenuntergang'
            old_offer.body = 'Dein erster Abend über Frankfurt beginnt mit einem exklusiven Willkommensgetränk.'
            old_offer.venue = beach
            old_offer.target = Offer.Target.ALL
            old_offer.save()
        else:
            Offer.objects.update_or_create(
                business=business,
                title='Willkommen zum Sonnenuntergang',
                defaults={
                    'venue': beach,
                    'body': 'Dein erster Abend über Frankfurt beginnt mit einem exklusiven Willkommensgetränk.',
                    'target': Offer.Target.ALL,
                    'created_by': owner,
                },
            )

        old_special = Offer.objects.filter(business=business, title='Skyline Member Special').first()
        if old_special:
            old_special.title = 'Besonderer Vorteil für Panorama-Mitglieder'
            old_special.body = 'Exklusive Vorteile für Liegen und Veranstaltungen der Stufe Panorama.'
            old_special.venue = beach
            old_special.target = Offer.Target.SKYLINE
            old_special.save()
        else:
            Offer.objects.update_or_create(
                business=business,
                title='Besonderer Vorteil für Panorama-Mitglieder',
                defaults={
                    'venue': beach,
                    'body': 'Exklusive Vorteile für Liegen und Veranstaltungen der Stufe Panorama.',
                    'target': Offer.Target.SKYLINE,
                    'created_by': owner,
                },
            )

        self.stdout.write(self.style.SUCCESS('CityBeach-Demodaten sind bereit.'))
