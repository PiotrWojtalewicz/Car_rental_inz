from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Car
from .forms import CarForm  # Załóżmy, że przygotujemy formularz dla modelu Car

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