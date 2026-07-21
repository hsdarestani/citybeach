from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import BusinessSettings, LedgerEntry, Membership, Notification, PaymentRequest, Wallet

OWNER_ROLES = {Membership.Role.OWNER, Membership.Role.MANAGER}
STAFF_ROLES = {Membership.Role.OWNER, Membership.Role.MANAGER, Membership.Role.STAFF}


def membership_for(user):
    if not user.is_authenticated:
        return None
    return Membership.objects.filter(user=user, is_active=True).select_related('business').first()


def require_role(user, business, roles):
    membership = Membership.objects.filter(user=user, business=business, is_active=True, role__in=roles).first()
    if not membership:
        raise PermissionDenied
    return membership


def settings_for(business):
    obj, _ = BusinessSettings.objects.get_or_create(business=business)
    return obj


def money(value):
    try:
        amount = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception as exc:
        raise ValidationError('Ungültiger Betrag.') from exc
    if amount <= 0:
        raise ValidationError('Der Betrag muss größer als 0 sein.')
    return amount


def recalculate_tier(wallet, settings_obj=None):
    settings_obj = settings_obj or settings_for(wallet.business)
    if wallet.monthly_topup >= settings_obj.skyline_threshold:
        wallet.tier = Wallet.Tier.SKYLINE
    elif wallet.monthly_topup >= settings_obj.sunset_threshold:
        wallet.tier = Wallet.Tier.SUNSET
    else:
        wallet.tier = Wallet.Tier.BEACH


def post_entry(*, wallet, entry_type, amount, actor, venue=None, description='', order_reference='', payment_request=None):
    amount = money(amount)
    allowed_roles = OWNER_ROLES if entry_type in {LedgerEntry.Type.TOPUP, LedgerEntry.Type.REFUND, LedgerEntry.Type.BONUS} else STAFF_ROLES
    require_role(actor, wallet.business, allowed_roles)
    with transaction.atomic():
        locked = Wallet.objects.select_for_update().get(pk=wallet.pk)
        before = locked.balance
        if entry_type in {LedgerEntry.Type.TOPUP, LedgerEntry.Type.REFUND, LedgerEntry.Type.BONUS}:
            after = before + amount
        else:
            if before < amount:
                raise ValidationError('Nicht genügend Guthaben.')
            after = before - amount
        locked.balance = after
        if entry_type == LedgerEntry.Type.TOPUP:
            locked.monthly_topup += amount
            recalculate_tier(locked)
        locked.save(update_fields=['balance', 'monthly_topup', 'tier', 'updated_at'])
        return LedgerEntry.objects.create(
            business=locked.business,
            venue=venue,
            wallet=locked,
            payment_request=payment_request,
            entry_type=entry_type,
            amount=amount,
            balance_before=before,
            balance_after=after,
            description=description,
            order_reference=order_reference,
            performed_by=actor,
        )


def notify_owners(payment):
    settings_obj = settings_for(payment.business)
    if not settings_obj.payment_notifications:
        return
    owners = Membership.objects.filter(
        business=payment.business,
        role=Membership.Role.OWNER,
        is_active=True,
    ).select_related('user')
    for membership in owners:
        Notification.objects.create(
            recipient=membership.user,
            business=payment.business,
            venue=payment.venue,
            kind=Notification.Kind.PAYMENT,
            title='Neue CityBeach-Zahlung',
            body=f'{payment.wallet.display_name} · {payment.total:.2f} € · {payment.venue.name}',
        )


def finalize_payment(payment, actor, tip_percentage=Decimal('0')):
    with transaction.atomic():
        payment = PaymentRequest.objects.select_for_update().select_related('wallet', 'business', 'venue').get(pk=payment.pk)
        if payment.status != PaymentRequest.Status.PENDING:
            raise ValidationError('Diese Zahlung wurde bereits verarbeitet.')
        tip_percentage = Decimal(str(tip_percentage)).quantize(Decimal('0.01'))
        settings_obj = settings_for(payment.business)
        allowed = {Decimal(str(option)).quantize(Decimal('0.01')) for option in settings_obj.tip_options}
        if tip_percentage not in allowed:
            raise ValidationError('Diese Trinkgeld-Auswahl ist nicht erlaubt.')
        payment.tip_percentage = tip_percentage
        payment.tip_amount = (payment.base_amount * tip_percentage / Decimal('100')).quantize(Decimal('0.01'))
        if payment.wallet.balance < payment.total:
            raise ValidationError('Nicht genügend Guthaben einschließlich Trinkgeld.')
        post_entry(
            wallet=payment.wallet,
            venue=payment.venue,
            entry_type=LedgerEntry.Type.PURCHASE,
            amount=payment.base_amount,
            actor=payment.created_by,
            description=payment.description or 'CityBeach-Zahlung',
            order_reference=payment.order_reference,
            payment_request=payment,
        )
        if payment.tip_amount > 0:
            post_entry(
                wallet=payment.wallet,
                venue=payment.venue,
                entry_type=LedgerEntry.Type.TIP,
                amount=payment.tip_amount,
                actor=payment.created_by,
                description='Trinkgeld',
                order_reference=payment.order_reference,
                payment_request=payment,
            )
        payment.status = PaymentRequest.Status.CONFIRMED
        payment.confirmed_at = timezone.now()
        payment.save(update_fields=['tip_percentage', 'tip_amount', 'status', 'confirmed_at'])
        notify_owners(payment)
        return payment


def create_payment(*, wallet, venue, actor, amount, description='', order_reference=''):
    require_role(actor, wallet.business, STAFF_ROLES)
    wallet = Wallet.objects.select_related('business').get(pk=wallet.pk)
    if wallet.status != Wallet.Status.ACTIVE:
        raise ValidationError('Diese Mitgliedskarte ist gesperrt.')
    amount = money(amount)
    if wallet.balance < amount:
        raise ValidationError('Nicht genügend Guthaben.')
    settings_obj = settings_for(wallet.business)
    payment = PaymentRequest.objects.create(
        business=wallet.business,
        venue=venue,
        wallet=wallet,
        created_by=actor,
        base_amount=amount,
        description=description,
        order_reference=order_reference,
        confirmation_required=settings_obj.require_customer_confirmation,
    )
    if not payment.confirmation_required:
        payment = finalize_payment(payment, actor, settings_obj.tip_1)
    return payment
