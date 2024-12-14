from django import forms
from .models import Car
#
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'rental_price', 'is_available', 'representative']


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
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")