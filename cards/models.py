import secrets
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


def member_number():
    return str(secrets.randbelow(90_000_000) + 10_000_000)


def receipt_number():
    return f"CB-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"


class Business(models.Model):
    name = models.CharField(max_length=140, default='CityBeach Frankfurt')
    slug = models.SlugField(unique=True, default='citybeach-frankfurt')
    currency = models.CharField(max_length=3, default='EUR')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Betrieb'
        verbose_name_plural = 'Betriebe'

    def __str__(self):
        return self.name


class Venue(models.Model):
    class Theme(models.TextChoices):
        BEACH = 'BEACH', 'CityBeach'
        ALM = 'ALM', 'CityAlm'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=80)
    theme = models.CharField(max_length=12, choices=Theme.choices, default=Theme.BEACH)
    subtitle = models.CharField(max_length=180, blank=True)
    address = models.TextField(blank=True)
    opening_hours = models.CharField(max_length=240, blank=True)
    website_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    google_review_url = models.URLField(blank=True)
    reservation_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position', 'name']
        constraints = [models.UniqueConstraint(fields=['business', 'slug'], name='unique_citybeach_venue_slug')]
        verbose_name = 'Bereich'
        verbose_name_plural = 'Bereiche'

    def __str__(self):
        return self.name


class BusinessSettings(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='settings')
    require_customer_confirmation = models.BooleanField(default=True)
    tip_1 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    tip_2 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5'))
    tip_3 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10'))
    tip_4 = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15'))
    sunset_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('250'))
    skyline_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('600'))
    birthday_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('10'))
    payment_notifications = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Anwendungseinstellung'
        verbose_name_plural = 'Anwendungseinstellungen'

    @property
    def tip_options(self):
        return [self.tip_1, self.tip_2, self.tip_3, self.tip_4]

    def __str__(self):
        return f'Einstellungen · {self.business}'


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Inhaber'
        MANAGER = 'MANAGER', 'Leitung'
        STAFF = 'STAFF', 'Mitarbeiter'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citybeach_memberships')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=12, choices=Role.choices)
    can_manage_content = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'business'], name='unique_citybeach_membership')]
        verbose_name = 'Zugriffsrolle'
        verbose_name_plural = 'Zugriffsrollen'

    def __str__(self):
        return f'{self.user} · {self.get_role_display()}'


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citybeach_profile')
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email_verified = models.BooleanField(default=False)
    selected_venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='selected_customers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kundenprofil'
        verbose_name_plural = 'Kundenprofile'

    def __str__(self):
        return f'Kundenprofil · {self.user}'


class Wallet(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Aktiv'
        BLOCKED = 'BLOCKED', 'Gesperrt'

    class Tier(models.TextChoices):
        BEACH = 'BEACH', 'Strand'
        SUNSET = 'SUNSET', 'Sonnenuntergang'
        SKYLINE = 'SKYLINE', 'Panorama'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name='wallets')
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='citybeach_wallet')
    member_number = models.CharField(max_length=8, unique=True, default=member_number, editable=False, db_index=True)
    display_name = models.CharField(max_length=140)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    tier = models.CharField(max_length=12, choices=Tier.choices, default=Tier.BEACH)
    monthly_topup = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Guthabenkonto'
        verbose_name_plural = 'Guthabenkonten'

    def __str__(self):
        return f'{self.member_number} · {self.display_name}'


class PaymentRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Wartet auf Bestätigung'
        CONFIRMED = 'CONFIRMED', 'Bezahlt'
        CANCELLED = 'CANCELLED', 'Storniert'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name='payment_requests')
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='payment_requests')
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='payment_requests')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citybeach_payments_created')
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tip_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    tip_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    description = models.CharField(max_length=255, blank=True)
    order_reference = models.CharField(max_length=100, blank=True)
    confirmation_required = models.BooleanField(default=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Zahlungsanforderung'
        verbose_name_plural = 'Zahlungsanforderungen'

    @property
    def total(self):
        return self.base_amount + self.tip_amount


class LedgerEntry(models.Model):
    class Type(models.TextChoices):
        TOPUP = 'TOPUP', 'Aufladung'
        PURCHASE = 'PURCHASE', 'Zahlung'
        TIP = 'TIP', 'Trinkgeld'
        REFUND = 'REFUND', 'Rückerstattung'
        BONUS = 'BONUS', 'Bonus'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=32, unique=True, default=receipt_number, editable=False, db_index=True)
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name='entries')
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, null=True, blank=True, related_name='entries')
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='entries')
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    entry_type = models.CharField(max_length=16, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    order_reference = models.CharField(max_length=100, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citybeach_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=~Q(amount=0), name='citybeach_entry_nonzero')]
        verbose_name = 'Buchung'
        verbose_name_plural = 'Buchungen'

    def __str__(self):
        return f'{self.get_entry_type_display()} · {self.amount} €'


class Offer(models.Model):
    class Target(models.TextChoices):
        ALL = 'ALL', 'Alle Mitglieder'
        BEACH = 'BEACH', 'Strand-Mitglieder'
        SUNSET = 'SUNSET', 'Sonnenuntergang-Mitglieder'
        SKYLINE = 'SKYLINE', 'Panorama-Mitglieder'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='offers')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, null=True, blank=True, related_name='offers')
    title = models.CharField(max_length=180)
    body = models.TextField()
    image = models.ImageField(upload_to='offers/%Y/%m/', blank=True)
    target = models.CharField(max_length=12, choices=Target.choices, default=Target.ALL)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='citybeach_offers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Angebot'
        verbose_name_plural = 'Angebote'

    def __str__(self):
        return self.title


class Notification(models.Model):
    class Kind(models.TextChoices):
        PAYMENT = 'PAYMENT', 'Zahlung'
        OFFER = 'OFFER', 'Angebot'
        SYSTEM = 'SYSTEM', 'System'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citybeach_notifications')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='notifications')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.SYSTEM)
    title = models.CharField(max_length=160)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mitteilung'
        verbose_name_plural = 'Mitteilungen'

    def __str__(self):
        return self.title


class PushDevice(models.Model):
    class Platform(models.TextChoices):
        IOS = 'IOS', 'iOS'
        ANDROID = 'ANDROID', 'Android'
        WEB = 'WEB', 'Web-Anwendung'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citybeach_devices')
    platform = models.CharField(max_length=12, choices=Platform.choices)
    token = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Endgerät'
        verbose_name_plural = 'Endgeräte'

    def __str__(self):
        return f'{self.user} · {self.get_platform_display()}'
