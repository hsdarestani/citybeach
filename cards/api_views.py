from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, Offer, PaymentRequest, Venue, Wallet
from .serializers import DeviceSerializer, EntrySerializer, NotificationSerializer, OfferSerializer, PaymentSerializer, VenueSerializer, WalletSerializer
from .services import create_payment, finalize_payment, membership_for


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = membership_for(request.user)
        wallet = Wallet.objects.filter(owner=request.user).first()
        return Response({
            'id': request.user.id,
            'email': request.user.email,
            'name': request.user.get_full_name(),
            'rolle': membership.get_role_display() if membership else 'Kunde',
            'rollen_code': membership.role if membership else 'CUSTOMER',
            'guthabenkonto': WalletSerializer(wallet).data if wallet else None,
        })


class VenuesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = membership_for(request.user)
        wallet = Wallet.objects.filter(owner=request.user).first()
        current_business = membership.business if membership else wallet.business
        return Response(VenueSerializer(current_business.venues.filter(is_active=True), many=True).data)


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(WalletSerializer(get_object_or_404(Wallet, owner=request.user)).data)


class EntriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_object_or_404(Wallet, owner=request.user)
        return Response(EntrySerializer(wallet.entries.select_related('venue')[:100], many=True).data)


class OffersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = get_object_or_404(Wallet, owner=request.user)
        offers = Offer.objects.filter(business=wallet.business, is_active=True, target__in=[Offer.Target.ALL, wallet.tier])
        venue = request.query_params.get('venue')
        offers = offers.filter(venue_id=venue) | offers.filter(venue__isnull=True) if venue else offers
        return Response(OfferSerializer(offers[:50], many=True, context={'request': request}).data)


class PendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(PaymentSerializer(PaymentRequest.objects.filter(wallet__owner=request.user, status=PaymentRequest.Status.PENDING), many=True).data)


class ConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(PaymentRequest, pk=payment_id, wallet__owner=request.user)
        try:
            payment = finalize_payment(payment, request.user, request.data.get('tip_percentage', 0))
        except ValidationError as exc:
            return Response({'fehler': exc.messages}, status=400)
        return Response(PaymentSerializer(payment).data)


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(NotificationSerializer(request.user.citybeach_notifications.all()[:100], many=True).data)


class DeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(DeviceSerializer(serializer.save()).data, status=201)


class StaffPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership = membership_for(request.user)
        if not membership:
            return Response({'fehler': 'Keine Berechtigung.'}, status=403)
        wallet = get_object_or_404(Wallet, business=membership.business, qr_token=request.data.get('wallet_token'))
        venue = get_object_or_404(Venue, business=membership.business, pk=request.data.get('venue'))
        try:
            payment = create_payment(
                wallet=wallet,
                venue=venue,
                actor=request.user,
                amount=request.data.get('amount'),
                description=request.data.get('description', ''),
                order_reference=request.data.get('order_reference', ''),
            )
        except ValidationError as exc:
            return Response({'fehler': exc.messages}, status=400)
        code = status.HTTP_202_ACCEPTED if payment.status == PaymentRequest.Status.PENDING else 201
        return Response(PaymentSerializer(payment).data, status=code)
