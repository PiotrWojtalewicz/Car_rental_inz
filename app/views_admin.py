from django.contrib import admin

from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Car, Representative, Rental
from .forms import CarForm, RepresentativeForm


# Sprawdzenie, czy użytkownik jest administratorem (należy do grupy Admins)
def is_admin(user):
    return user.groups.filter(name='Admins').exists()


# Widok dodawania nowego samochodu
@login_required
@user_passes_test(is_admin)
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Przekierowanie do dashboardu po dodaniu
    else:
        form = CarForm()
    return render(request, 'app/add_car.html', {'form': form})


# Widok edycji istniejącego samochodu
@login_required
@user_passes_test(is_admin)
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
@login_required
@user_passes_test(is_admin)
def car_delete(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        car.delete()
        return redirect('car_list')
    return render(request, 'app/car_confirm_delete.html', {'car': car})


# Widok dodawania nowego przedstawiciela
@login_required
@user_passes_test(is_admin)
def add_representative(request):
    if request.method == 'POST':
        form = RepresentativeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Przekierowanie po dodaniu
    else:
        form = RepresentativeForm()
    return render(request, 'app/add_representative.html', {'form': form})


# Widok listy samochodów
@login_required
@user_passes_test(is_admin)
def car_list(request):
    cars = Car.objects.all()  # Pobranie wszystkich samochodów
    return render(request, 'app/car_list.html', {'cars': cars})


# Widok szczegółów samochodu
@login_required
@user_passes_test(is_admin)
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'app/car_detail.html', {'car': car})


# Widok przypisania samochodu do przedstawiciela
@login_required
@user_passes_test(is_admin)
def assign_representative(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    representatives = Representative.objects.all()

    if request.method == 'POST':
        representative_id = request.POST.get('representative')
        representative = get_object_or_404(Representative, id=representative_id)
        car.representative = representative
        car.save()
        return redirect('car_detail', car_id=car.id)

    return render(request, 'app/assign_representative.html', {'car': car, 'representatives': representatives})

