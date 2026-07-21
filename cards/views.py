import io
from decimal import Decimal

import qrcode
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AppleProfileCompletionForm, OfferForm, RegistrationForm, SettingsForm, StaffPaymentForm, TopupForm
from .models import Business, CustomerProfile, LedgerEntry, Offer, PaymentRequest, Wallet
from .services import OWNER_ROLES, STAFF_ROLES, create_payment, finalize_payment, membership_for, post_entry, settings_for


def business():
    return Business.objects.first()


def landing(request):
    current_business = business()
    venues = current_business.venues.filter(is_active=True) if current_business else []
    offers = Offer.objects.filter(is_active=True).select_related('venue')[:6]
    return render(request, 'cards/landing.html', {'business': current_business, 'venues': venues, 'offers': offers})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.username = form.cleaned_data['email'].lower()
        user.email = user.username
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        current_business = business()
        CustomerProfile.objects.create(
            user=user,
            phone=form.cleaned_data['phone'],
            birth_date=form.cleaned_data['birth_date'],
            email_verified=True,
            selected_venue=current_business.venues.filter(is_active=True).first(),
        )
        Wallet.objects.create(
            business=current_business,
            owner=user,
            display_name=f'{user.first_name} {user.last_name}'.strip() or user.email,
            email=user.email,
            phone=form.cleaned_data['phone'],
        )
        login(request, user)
        messages.success(request, 'Willkommen über den Dächern Frankfurts!')
        return redirect('dashboard')
    return render(request, 'cards/register.html', {'form': form})


@login_required
def complete_customer_profile(request):
    membership = membership_for(request.user)
    if membership:
        return redirect('dashboard')

    current_business = business()
    profile, _ = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'email_verified': True,
            'selected_venue': current_business.venues.filter(is_active=True).first() if current_business else None,
        },
    )
    form = AppleProfileCompletionForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.email_verified = True
        if profile.selected_venue_id is None and current_business:
            profile.selected_venue = current_business.venues.filter(is_active=True).first()
        profile.save()

        display_name = request.user.get_full_name().strip() or request.user.email or 'CityBeach-Mitglied'
        wallet, _ = Wallet.objects.get_or_create(
            owner=request.user,
            defaults={
                'business': current_business,
                'display_name': display_name,
                'email': request.user.email,
                'phone': profile.phone,
            },
        )
        wallet.display_name = display_name
        wallet.email = request.user.email
        wallet.phone = profile.phone
        wallet.save(update_fields=['display_name', 'email', 'phone', 'updated_at'])
        messages.success(request, 'Dein Kundenprofil ist vollständig eingerichtet.')
        return redirect('customer_dashboard')
    return render(request, 'cards/complete_profile.html', {'form': form})


@login_required
def dashboard(request):
    membership = membership_for(request.user)
    if membership and membership.role in OWNER_ROLES:
        return redirect('owner_dashboard')
    if membership and membership.role in STAFF_ROLES:
        return redirect('staff_dashboard')
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if not profile.phone or not profile.birth_date:
        return redirect('complete_customer_profile')
    return redirect('customer_dashboard')


@login_required
def customer_dashboard(request):
    wallet = get_object_or_404(Wallet.objects.select_related('business', 'owner'), owner=request.user)
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    venues = wallet.business.venues.filter(is_active=True)
    selected_id = request.GET.get('venue') or (str(profile.selected_venue_id) if profile.selected_venue_id else '')
    selected = venues.filter(pk=selected_id).first() or venues.first()
    if selected and profile.selected_venue_id != selected.id:
        profile.selected_venue = selected
        profile.save(update_fields=['selected_venue'])
    now = timezone.now()
    offers = Offer.objects.filter(
        business=wallet.business,
        is_active=True,
        target__in=[Offer.Target.ALL, wallet.tier],
    ).filter(
        Q(venue__isnull=True) | Q(venue=selected),
    ).filter(
        Q(starts_at__isnull=True) | Q(starts_at__lte=now),
    ).filter(
        Q(ends_at__isnull=True) | Q(ends_at__gte=now),
    )[:8]
    pending = wallet.payment_requests.filter(status=PaymentRequest.Status.PENDING).select_related('venue').first()
    return render(request, 'cards/customer_dashboard.html', {
        'wallet': wallet,
        'profile': profile,
        'venues': venues,
        'selected': selected,
        'offers': offers,
        'pending': pending,
        'entries': wallet.entries.select_related('venue')[:12],
        'tip_options': settings_for(wallet.business).tip_options,
        'notifications': request.user.citybeach_notifications.all()[:8],
    })


@login_required
@require_POST
def confirm_payment_view(request, payment_id):
    payment = get_object_or_404(
        PaymentRequest,
        pk=payment_id,
        wallet__owner=request.user,
        status=PaymentRequest.Status.PENDING,
    )
    try:
        finalize_payment(payment, request.user, request.POST.get('tip_percentage', '0'))
        messages.success(request, 'Zahlung bestätigt. Danke und genieße die Aussicht!')
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    return redirect('customer_dashboard')


@login_required
def qr_card(request):
    wallet = get_object_or_404(Wallet, owner=request.user)
    image = qrcode.make(str(wallet.qr_token))
    output = io.BytesIO()
    image.save(output, format='PNG')
    return HttpResponse(output.getvalue(), content_type='image/png')


@login_required
def staff_dashboard(request):
    membership = membership_for(request.user)
    if not membership or membership.role not in STAFF_ROLES:
        raise PermissionDenied
    form = StaffPaymentForm(request.POST or None, business=membership.business)
    if request.method == 'POST' and form.is_valid():
        wallet = get_object_or_404(Wallet, business=membership.business, qr_token=form.cleaned_data['qr_token'])
        try:
            payment = create_payment(
                wallet=wallet,
                venue=form.cleaned_data['venue'],
                actor=request.user,
                amount=form.cleaned_data['amount'],
                description=form.cleaned_data['description'],
                order_reference=form.cleaned_data['order_reference'],
            )
            messages.success(
                request,
                'Zahlung wartet auf Bestätigung des Gastes.'
                if payment.status == PaymentRequest.Status.PENDING
                else 'Zahlung erfolgreich abgeschlossen.',
            )
            return redirect('staff_dashboard')
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
    return render(request, 'cards/staff_dashboard.html', {
        'form': form,
        'membership': membership,
        'recent': membership.business.payment_requests.select_related('wallet', 'venue')[:12],
        'venues': membership.business.venues.filter(is_active=True),
    })


@login_required
def owner_dashboard(request):
    membership = membership_for(request.user)
    if not membership or membership.role not in OWNER_ROLES:
        raise PermissionDenied
    query = request.GET.get('q', '').strip()
    wallets = membership.business.wallets.all()
    if query:
        wallets = wallets.filter(
            Q(display_name__icontains=query)
            | Q(member_number__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    return render(request, 'cards/owner_dashboard.html', {
        'membership': membership,
        'wallets': wallets[:50],
        'wallet_count': membership.business.wallets.count(),
        'total_balance': membership.business.wallets.aggregate(v=Sum('balance'))['v'] or 0,
        'recent': membership.business.entries.select_related('wallet', 'venue')[:15],
        'notifications': request.user.citybeach_notifications.all()[:15],
        'venues': membership.business.venues.filter(is_active=True),
        'offers': membership.business.offers.all()[:8],
    })


@login_required
def wallet_detail(request, wallet_id):
    membership = membership_for(request.user)
    if not membership or membership.role not in OWNER_ROLES:
        raise PermissionDenied
    wallet = get_object_or_404(Wallet, business=membership.business, pk=wallet_id)
    form = TopupForm(request.POST or None, business=membership.business)
    if request.method == 'POST' and form.is_valid():
        entry_type = LedgerEntry.Type.REFUND if request.POST.get('action') == 'refund' else LedgerEntry.Type.TOPUP
        try:
            post_entry(
                wallet=wallet,
                venue=form.cleaned_data['venue'],
                entry_type=entry_type,
                amount=form.cleaned_data['amount'],
                actor=request.user,
                description=form.cleaned_data['description'],
            )
            messages.success(request, 'Guthaben wurde aktualisiert.')
            return redirect('wallet_detail', wallet_id=wallet.id)
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
    return render(request, 'cards/wallet_detail.html', {
        'wallet': wallet,
        'form': form,
        'entries': wallet.entries.select_related('venue')[:30],
    })


@login_required
@require_POST
def toggle_wallet(request, wallet_id):
    membership = membership_for(request.user)
    if not membership or membership.role not in OWNER_ROLES:
        raise PermissionDenied
    wallet = get_object_or_404(Wallet, business=membership.business, pk=wallet_id)
    wallet.status = Wallet.Status.BLOCKED if wallet.status == Wallet.Status.ACTIVE else Wallet.Status.ACTIVE
    wallet.save(update_fields=['status', 'updated_at'])
    return redirect('wallet_detail', wallet_id=wallet.id)


@login_required
def owner_content(request):
    membership = membership_for(request.user)
    if not membership or (membership.role not in OWNER_ROLES and not membership.can_manage_content):
        raise PermissionDenied
    settings_obj = settings_for(membership.business)
    settings_form = SettingsForm(request.POST or None, instance=settings_obj, prefix='settings')
    offer_form = OfferForm(request.POST or None, request.FILES or None, business=membership.business, prefix='offer')
    if request.method == 'POST':
        if 'save_settings' in request.POST and settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Einstellungen der Anwendung gespeichert.')
            return redirect('owner_content')
        if 'create_offer' in request.POST and offer_form.is_valid():
            offer = offer_form.save(commit=False)
            offer.business = membership.business
            offer.created_by = request.user
            offer.save()
            messages.success(request, 'Angebot veröffentlicht.')
            return redirect('owner_content')
    return render(request, 'cards/owner_content.html', {
        'settings_form': settings_form,
        'offer_form': offer_form,
        'offers': membership.business.offers.select_related('venue')[:30],
        'venues': membership.business.venues.all(),
    })


@login_required
def receipt(request, entry_id):
    entry = get_object_or_404(
        LedgerEntry.objects.select_related('wallet', 'venue', 'performed_by', 'business'),
        pk=entry_id,
    )
    membership = membership_for(request.user)
    if entry.wallet.owner_id != request.user.id and (not membership or membership.business_id != entry.business_id):
        raise PermissionDenied
    return render(request, 'cards/receipt.html', {'entry': entry})


def health(request):
    return JsonResponse({'zustand': 'bereit', 'anwendung': 'citybeach-frankfurt'})


def manifest_view(request):
    return JsonResponse({
        'name': 'CityBeach Frankfurt',
        'short_name': 'CityBeach',
        'start_url': '/dashboard/',
        'display': 'standalone',
        'background_color': '#071015',
        'theme_color': '#f7a825',
        'lang': 'de-DE',
        'description': 'Digitale Mitgliedskarte und Guthabenkonto für CityBeach Frankfurt.',
        'icons': [{'src': '/static/cards/icon.svg', 'sizes': '180x180', 'type': 'image/svg+xml'}],
    })


def service_worker_view(request):
    return HttpResponse(
        "self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('fetch',()=>{});",
        content_type='application/javascript',
    )
