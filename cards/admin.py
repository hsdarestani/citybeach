from django.contrib import admin

from .models import Business, BusinessSettings, CustomerProfile, LedgerEntry, Membership, Notification, Offer, PaymentRequest, PushDevice, Venue, Wallet

admin.site.site_header = 'CityBeach-Verwaltung'
admin.site.site_title = 'CityBeach-Verwaltung'
admin.site.index_title = 'Betrieb, Mitglieder und Inhalte verwalten'


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'currency', 'created_at')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'theme', 'is_active', 'position')
    list_filter = ('theme', 'is_active')


@admin.register(BusinessSettings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('business', 'require_customer_confirmation', 'sunset_threshold', 'skyline_threshold', 'payment_notifications')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'role', 'can_manage_content', 'is_active')
    list_filter = ('role', 'is_active')


@admin.register(CustomerProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'phone', 'selected_venue')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('member_number', 'display_name', 'tier', 'monthly_topup', 'balance', 'status')
    search_fields = ('member_number', 'display_name', 'email', 'phone')


@admin.register(PaymentRequest)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'wallet', 'venue', 'base_amount', 'tip_amount', 'status', 'created_by')
    list_filter = ('status', 'venue')


@admin.register(LedgerEntry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'receipt_number', 'wallet', 'venue', 'entry_type', 'amount', 'balance_after', 'performed_by')
    list_filter = ('entry_type', 'venue')
    readonly_fields = [field.name for field in LedgerEntry._meta.fields]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'target', 'is_active', 'starts_at', 'ends_at')
    list_filter = ('venue', 'target', 'is_active')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'recipient', 'kind', 'venue', 'is_read')


@admin.register(PushDevice)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'is_active', 'updated_at')
