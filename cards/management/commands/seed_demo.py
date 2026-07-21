import os
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from cards.models import Business, BusinessSettings, CustomerProfile, LedgerEntry, Membership, Offer, Venue, Wallet
from cards.services import post_entry

class Command(BaseCommand):
    help='Create CityBeach demo data idempotently.'
    def handle(self,*args,**options):
        User=get_user_model()
        business,_=Business.objects.get_or_create(slug='citybeach-frankfurt',defaults={'name':'CityBeach Frankfurt','currency':'EUR'})
        BusinessSettings.objects.get_or_create(business=business)
        beach,_=Venue.objects.get_or_create(business=business,slug='citybeach',defaults={'name':'CityBeach Frankfurt','theme':Venue.Theme.BEACH,'subtitle':'Summer lives above the city','address':'Carl-Theodor-Reiffenstein-Platz 5, 60313 Frankfurt am Main · Zugang über Töngesgasse 8','opening_hours':'So–Mi 12–22 Uhr · Do–Sa 12–00 Uhr · nur bei gutem Wetter','website_url':'https://www.citybeach-frankfurt.de/','instagram_url':'https://www.instagram.com/citybeachfrankfurt/','reservation_url':'https://www.citybeach-frankfurt.de/','position':1})
        Venue.objects.get_or_create(business=business,slug='cityalm',defaults={'name':'CityAlm Frankfurt','theme':Venue.Theme.ALM,'subtitle':'Winterzauber über den Dächern Frankfurts','address':'Carl-Theodor-Reiffenstein-Platz 5, 60313 Frankfurt am Main','website_url':'https://www.cityalm.de/','instagram_url':'https://www.instagram.com/citybeachfrankfurt/','position':2})
        owner_pwd=os.getenv('CITYBEACH_OWNER_PASSWORD','CityBeachOwner!2026'); staff_pwd=os.getenv('CITYBEACH_STAFF_PASSWORD','CityBeachStaff!2026'); customer_pwd=os.getenv('CITYBEACH_CUSTOMER_PASSWORD','CityBeachGuest!2026')
        owner,_=User.objects.get_or_create(username='owner',defaults={'email':'owner@citybeach.local','first_name':'CityBeach','last_name':'Owner'}); owner.set_password(owner_pwd); owner.is_staff=True; owner.is_superuser=True; owner.save()
        staff,_=User.objects.get_or_create(username='staff',defaults={'email':'staff@citybeach.local','first_name':'Beach','last_name':'Crew'}); staff.set_password(staff_pwd); staff.save()
        customer,_=User.objects.get_or_create(username='customer',defaults={'email':'customer@citybeach.local','first_name':'Sunny','last_name':'Guest'}); customer.set_password(customer_pwd); customer.save()
        Membership.objects.update_or_create(user=owner,business=business,defaults={'role':Membership.Role.OWNER,'is_active':True,'can_manage_content':True})
        Membership.objects.update_or_create(user=staff,business=business,defaults={'role':Membership.Role.STAFF,'is_active':True})
        CustomerProfile.objects.get_or_create(user=customer,defaults={'phone':'+49 170 0000000','selected_venue':beach,'email_verified':True})
        wallet,_=Wallet.objects.get_or_create(owner=customer,defaults={'business':business,'display_name':'Sunny Guest','email':customer.email,'phone':'+49 170 0000000'})
        if wallet.balance==0:
            post_entry(wallet=wallet,venue=beach,entry_type=LedgerEntry.Type.TOPUP,amount=Decimal('200'),actor=owner,description='Welcome Guthaben')
            post_entry(wallet=wallet,venue=beach,entry_type=LedgerEntry.Type.BONUS,amount=Decimal('20'),actor=owner,description='10% Welcome Bonus')
        Offer.objects.get_or_create(business=business,title='Sunset Welcome',defaults={'venue':beach,'body':'Dein erster Rooftop-Abend beginnt mit einem exklusiven Welcome Drink.','target':Offer.Target.ALL,'created_by':owner})
        Offer.objects.get_or_create(business=business,title='Skyline Member Special',defaults={'venue':beach,'body':'Exklusive Daybed- und Event-Vorteile für Skyline Member.','target':Offer.Target.SKYLINE,'created_by':owner})
        self.stdout.write(self.style.SUCCESS('CityBeach demo data ready.'))
