import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Wallet
from .services import OWNER_ROLES, membership_for


UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
    re.IGNORECASE,
)


@login_required
def owner_wallet_scan(request):
    membership = membership_for(request.user)
    if not membership or membership.role not in OWNER_ROLES:
        raise PermissionDenied

    raw_value = request.GET.get("token", "").strip()
    match = UUID_PATTERN.search(raw_value)
    if match is None:
        messages.error(request, "Der QR-Code enthält keinen gültigen Kartencode.")
        return redirect("owner_dashboard")

    wallet = Wallet.objects.filter(
        business=membership.business,
        qr_token=match.group(0),
    ).first()
    if wallet is None:
        messages.error(
            request,
            "Die Mitgliedskarte wurde nicht gefunden oder gehört zu einem anderen Betrieb.",
        )
        return redirect("owner_dashboard")

    return redirect("wallet_detail", wallet_id=wallet.pk)
