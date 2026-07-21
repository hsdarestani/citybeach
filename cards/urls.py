from django.urls import path
from . import api_views, views
urlpatterns=[
 path('',views.landing,name='landing'),path('health/',views.health,name='health'),path('accounts/register/',views.register,name='register'),
 path('dashboard/',views.dashboard,name='dashboard'),path('app/',views.customer_dashboard,name='customer_dashboard'),path('app/card.png',views.qr_card,name='qr_card'),
 path('app/payments/<uuid:payment_id>/confirm/',views.confirm_payment_view,name='confirm_payment'),
 path('staff/',views.staff_dashboard,name='staff_dashboard'),path('owner/',views.owner_dashboard,name='owner_dashboard'),path('owner/content/',views.owner_content,name='owner_content'),
 path('owner/wallet/<uuid:wallet_id>/',views.wallet_detail,name='wallet_detail'),path('owner/wallet/<uuid:wallet_id>/toggle/',views.toggle_wallet,name='toggle_wallet'),
 path('receipt/<uuid:entry_id>/',views.receipt,name='receipt'),
 path('api/v1/me/',api_views.MeView.as_view()),path('api/v1/venues/',api_views.VenuesView.as_view()),path('api/v1/wallet/',api_views.WalletView.as_view()),path('api/v1/entries/',api_views.EntriesView.as_view()),path('api/v1/offers/',api_views.OffersView.as_view()),path('api/v1/payments/pending/',api_views.PendingView.as_view()),path('api/v1/payments/<uuid:payment_id>/confirm/',api_views.ConfirmView.as_view()),path('api/v1/notifications/',api_views.NotificationsView.as_view()),path('api/v1/devices/',api_views.DeviceView.as_view()),path('api/v1/staff/payments/',api_views.StaffPaymentView.as_view()),
]
