from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import BusinessSettings, Offer, Venue, Wallet

class RegistrationForm(UserCreationForm):
    first_name=forms.CharField(label='Vorname',max_length=150)
    last_name=forms.CharField(label='Nachname',max_length=150)
    email=forms.EmailField(label='E-Mail')
    phone=forms.CharField(label='Mobilnummer',max_length=40)
    birth_date=forms.DateField(label='Geburtsdatum',widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model=get_user_model(); fields=('first_name','last_name','email','phone','birth_date','password1','password2')
    def clean_email(self):
        email=self.cleaned_data['email'].lower()
        if get_user_model().objects.filter(username__iexact=email).exists(): raise forms.ValidationError('Diese E-Mail ist bereits registriert.')
        return email

class StaffPaymentForm(forms.Form):
    qr_token=forms.UUIDField(label='Member Card Code')
    venue=forms.ModelChoiceField(queryset=Venue.objects.none(),label='Bereich')
    amount=forms.DecimalField(label='Betrag',max_digits=12,decimal_places=2,min_value=0.01)
    description=forms.CharField(label='Bestellung',required=False,max_length=255)
    order_reference=forms.CharField(label='Kassen-/Bestellnummer',required=False,max_length=100)
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business: self.fields['venue'].queryset=business.venues.filter(is_active=True)

class TopupForm(forms.Form):
    amount=forms.DecimalField(label='Betrag',max_digits=12,decimal_places=2,min_value=0.01)
    venue=forms.ModelChoiceField(queryset=Venue.objects.none(),label='Bereich',required=False)
    description=forms.CharField(label='Notiz',required=False,max_length=255)
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business: self.fields['venue'].queryset=business.venues.filter(is_active=True)

class WalletForm(forms.ModelForm):
    class Meta: model=Wallet; fields=('display_name','email','phone')

class SettingsForm(forms.ModelForm):
    class Meta:
        model=BusinessSettings
        fields=('require_customer_confirmation','tip_1','tip_2','tip_3','tip_4','sunset_threshold','skyline_threshold','birthday_bonus','payment_notifications')

class OfferForm(forms.ModelForm):
    class Meta:
        model=Offer
        fields=('venue','title','body','image','target','starts_at','ends_at','is_active')
        widgets={'starts_at':forms.DateTimeInput(attrs={'type':'datetime-local'}),'ends_at':forms.DateTimeInput(attrs={'type':'datetime-local'}),'body':forms.Textarea(attrs={'rows':4})}
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business: self.fields['venue'].queryset=business.venues.filter(is_active=True)
