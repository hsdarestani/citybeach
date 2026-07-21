from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import BusinessSettings, CustomerProfile, Offer, Venue, Wallet


def validate_adult(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 18:
        raise forms.ValidationError('Du musst mindestens 18 Jahre alt sein.')
    return birth_date


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Vorname', max_length=150)
    last_name = forms.CharField(label='Nachname', max_length=150)
    email = forms.EmailField(label='E-Mail-Adresse')
    phone = forms.CharField(label='Mobilnummer', max_length=40)
    birth_date = forms.DateField(label='Geburtsdatum', widget=forms.DateInput(attrs={'type': 'date'}))
    age_confirmed = forms.BooleanField(label='Ich bestätige, dass ich mindestens 18 Jahre alt bin.')

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'age_confirmed', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if get_user_model().objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('Diese E-Mail-Adresse ist bereits registriert.')
        return email

    def clean_birth_date(self):
        return validate_adult(self.cleaned_data['birth_date'])


class AppleProfileCompletionForm(forms.ModelForm):
    age_confirmed = forms.BooleanField(label='Ich bestätige, dass ich mindestens 18 Jahre alt bin.')

    class Meta:
        model = CustomerProfile
        fields = ('phone', 'birth_date', 'age_confirmed')
        labels = {'phone': 'Mobilnummer', 'birth_date': 'Geburtsdatum'}
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}

    def clean_birth_date(self):
        return validate_adult(self.cleaned_data['birth_date'])


class StaffPaymentForm(forms.Form):
    qr_token = forms.UUIDField(label='Code der Mitgliedskarte')
    venue = forms.ModelChoiceField(queryset=Venue.objects.none(), label='Bereich')
    amount = forms.DecimalField(label='Betrag', max_digits=12, decimal_places=2, min_value=0.01)
    description = forms.CharField(label='Bestellung', required=False, max_length=255)
    order_reference = forms.CharField(label='Kassen- oder Bestellnummer', required=False, max_length=100)

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            self.fields['venue'].queryset = business.venues.filter(is_active=True)


class TopupForm(forms.Form):
    amount = forms.DecimalField(label='Betrag', max_digits=12, decimal_places=2, min_value=0.01)
    venue = forms.ModelChoiceField(queryset=Venue.objects.none(), label='Bereich', required=False)
    description = forms.CharField(label='Notiz', required=False, max_length=255)

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            self.fields['venue'].queryset = business.venues.filter(is_active=True)


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('display_name', 'email', 'phone')
        labels = {'display_name': 'Anzeigename', 'email': 'E-Mail-Adresse', 'phone': 'Mobilnummer'}


class SettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = (
            'require_customer_confirmation',
            'tip_1',
            'tip_2',
            'tip_3',
            'tip_4',
            'sunset_threshold',
            'skyline_threshold',
            'birthday_bonus',
            'payment_notifications',
        )
        labels = {
            'require_customer_confirmation': 'Bestätigung durch den Gast erforderlich',
            'tip_1': 'Erste Trinkgeld-Auswahl in Prozent',
            'tip_2': 'Zweite Trinkgeld-Auswahl in Prozent',
            'tip_3': 'Dritte Trinkgeld-Auswahl in Prozent',
            'tip_4': 'Vierte Trinkgeld-Auswahl in Prozent',
            'sunset_threshold': 'Grenze für die Stufe Sonnenuntergang',
            'skyline_threshold': 'Grenze für die Stufe Panorama',
            'birthday_bonus': 'Geburtstagsbonus',
            'payment_notifications': 'Mitteilung bei jeder Zahlung',
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('venue', 'title', 'body', 'image', 'target', 'starts_at', 'ends_at', 'is_active')
        labels = {
            'venue': 'Bereich',
            'title': 'Titel',
            'body': 'Beschreibung',
            'image': 'Bild',
            'target': 'Zielgruppe',
            'starts_at': 'Beginn',
            'ends_at': 'Ende',
            'is_active': 'Sichtbar',
        }
        widgets = {
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'body': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            self.fields['venue'].queryset = business.venues.filter(is_active=True)
