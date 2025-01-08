from django.utils import timezone

from django import forms
from .models import Car, Rental
from django.contrib.auth.models import User
from django.forms import ModelForm
from datetime import timedelta
#
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'rental_price', 'is_available', 'representative']
        labels = {
            'brand': 'Marka',
            'model': 'Model',
            'year': 'Rok produkcji',
            'rental_price': 'Cena wypożyczenia',
            'is_available': 'Dostępny',
            'representative': 'Reprezentant',
        }
        widgets = {
            'rental_price': forms.NumberInput(attrs={'placeholder': 'Podaj cenę w PLN'}),
        }

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Potwierdź hasło'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Sprawdzenie, czy hasło zaczyna się od wielkiej litery
        if not password[0].isupper():
            raise ValidationError("Hasło musi zaczynać się od wielkiej litery.")

        # Sprawdzenie, czy hasło ma co najmniej 4 znaki
        if len(password) < 4:
            raise ValidationError("Hasło musi mieć co najmniej 4 znaki.")

        return password

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        # Sprawdzenie, czy hasła pasują
        if password != password_confirm:
            raise ValidationError("Hasła muszą być takie same.")

        return password_confirm


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nazwa użytkownika",
        widget=forms.TextInput(attrs={'placeholder': 'Podaj nazwę użytkownika'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Podaj hasło'}),
        label="Hasło"
    )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'car': 'Samochód',
            'start_date': 'Data rozpoczęcia',
            'end_date': 'Data zakończenia',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RentalForm(forms.ModelForm):
    accept_terms = forms.BooleanField(
        required=True,
        label="Akceptuję warunki wypożyczenia",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Musisz zaakceptować warunki wypożyczenia.'}
    )
    class Meta:
        model = Rental
        fields = ['car', 'start_date', 'end_date']
        labels = {
            'car': 'Samochód',
            'start_date': 'Data rozpoczęcia',
            'end_date': 'Data zakończenia',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(RentalForm, self).__init__(*args, **kwargs)
        # Domyślnie ustawić datę rozpoczęcia na dzisiaj
        today = timezone.now().date()
        self.fields['start_date'].initial = today
        # Dodać minimalną datę dla end_date, żeby nie można było ustawić daty zakończenia przed datą rozpoczęcia
        self.fields['end_date'].widget.attrs['min'] = today

