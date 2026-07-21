from rest_framework import serializers
from .models import LedgerEntry, Notification, Offer, PaymentRequest, PushDevice, Venue, Wallet

class VenueSerializer(serializers.ModelSerializer):
    class Meta: model=Venue; fields=('id','name','slug','theme','subtitle','address','opening_hours','website_url','instagram_url','google_review_url','reservation_url')
class WalletSerializer(serializers.ModelSerializer):
    tier_label=serializers.CharField(source='get_tier_display',read_only=True)
    class Meta: model=Wallet; fields=('id','member_number','display_name','balance','tier','tier_label','monthly_topup','status','qr_token')
class EntrySerializer(serializers.ModelSerializer):
    venue_name=serializers.CharField(source='venue.name',read_only=True,allow_null=True)
    class Meta: model=LedgerEntry; fields=('id','receipt_number','entry_type','amount','balance_before','balance_after','description','order_reference','venue_name','created_at')
class OfferSerializer(serializers.ModelSerializer):
    venue_name=serializers.CharField(source='venue.name',read_only=True,allow_null=True)
    image_url=serializers.SerializerMethodField()
    def get_image_url(self,obj):
        if not obj.image: return ''
        request=self.context.get('request'); return request.build_absolute_uri(obj.image.url) if request else obj.image.url
    class Meta: model=Offer; fields=('id','venue','venue_name','title','body','image_url','target','starts_at','ends_at')
class PaymentSerializer(serializers.ModelSerializer):
    total=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True)
    venue_name=serializers.CharField(source='venue.name',read_only=True)
    class Meta: model=PaymentRequest; fields=('id','venue','venue_name','base_amount','tip_percentage','tip_amount','total','description','order_reference','status','created_at')
class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model=Notification; fields=('id','kind','title','body','is_read','created_at')
class DeviceSerializer(serializers.ModelSerializer):
    class Meta: model=PushDevice; fields=('platform','token')
    def create(self,validated_data):
        obj,_=PushDevice.objects.update_or_create(token=validated_data['token'],defaults={'user':self.context['request'].user,'platform':validated_data['platform'],'is_active':True})
        return obj
