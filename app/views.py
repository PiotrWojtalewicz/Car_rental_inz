from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Car
from .forms import CarForm
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate
from .forms import LoginForm


def home(request):
    return HttpResponse("Witaj w naszej wypożyczalni samochodów!")
def car_list(request):
    cars = Car.objects.all()  # Pobranie wszystkich samochodów
    return render(request, 'app/car_list.html', {'cars': cars})


# Widok szczegółów samochodu
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'app/car_detail.html', {'car': car})


# Widok dodawania nowego samochodu
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('car_list')  # Przekierowanie na listę samochodów po zapisaniu
    else:
        form = CarForm()
    return render(request, 'app/car_form.html', {'form': form})


# Widok edycji istniejącego samochodu
def car_update(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    return render(request, 'app/car_form.html', {'form': form})


# Widok usuwania samochodu
def car_delete(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        car.delete()
        return redirect('car_list')
    return render(request, 'app/car_confirm_delete.html', {'car': car})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Tworzenie nowego użytkownika
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Ustawienie zahaszowanego hasła
            user.save()

            # Logowanie użytkownika po rejestracji
            user = authenticate(username=user.username, password=form.cleaned_data['password'])
            login(request, user)

            return redirect('home')  # Przekierowanie po udanej rejestracji
    else:
        form = RegistrationForm()

    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('car_list')  # Przekierowanie na stronę z listą samochodów (lub inną stronę)
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})

