from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Car, Rental,Representative
from .forms import CarForm
from .forms import RegistrationForm,ProfileEditForm
from django.contrib.auth import login, authenticate,logout
from .forms import LoginForm,RentalForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from datetime import datetime

def home(request):
    # return HttpResponse("Witaj w naszej wypożyczalni samochodów!")
    return render(request, 'app/home.html')
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
            return redirect('car_list')
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

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Ustawienie zahaszowanego hasła
            user.save()


            user = authenticate(username=user.username, password=form.cleaned_data['password'])
            login(request, user)

            return redirect('home')
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
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_dashboard(request):
    return render(request, 'app/dashboard.html', {'user': request.user})

def user_profile(request):
    return render(request, 'app/profile.html', {'user': request.user})


@login_required
def rental_history(request):
    current_date = timezone.now().date()
    active_rentals = Rental.objects.filter(user=request.user, end_date__gte=current_date)
    completed_rentals = Rental.objects.filter(user=request.user, end_date__lt=current_date)

    print("Dzisiejsza data:", current_date)
    print("Aktywne wypożyczenia:", active_rentals)
    print("Zakończone wypożyczenia:", completed_rentals)

    return render(request, 'app/rental_history.html', {
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
    })


def available_cars(request):
    # Pobierz dostępne samochody
    cars = Car.objects.filter(is_available=True)
    return render(request, 'app/available_cars.html', {'cars': cars})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'app/edit_profile.html', {'form': form})


@login_required
def rental_history(request):
    current_date = timezone.now().date()
    active_rentals = Rental.objects.filter(user=request.user, end_date__gte=current_date)
    completed_rentals = Rental.objects.filter(user=request.user, end_date__lt=current_date)

    print("Aktywne wypożyczenia:", active_rentals)
    print("Zakończone wypożyczenia:", completed_rentals)

    return render(request, 'app/rental_history.html', {
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
    })



@login_required
def user_rentals(request):
    rentals = Rental.objects.filter(user=request.user)

    # Sprawdź i zaktualizuj status każdego wypożyczenia
    for rental in rentals:
        rental.update_status()

    return render(request, 'app/rentals.html', {'rentals': rentals})

@login_required
def add_car(request):
    if request.method == 'POST':
        model = request.POST.get('model')
        brand = request.POST.get('brand')
        year = int(request.POST.get('year'))
        rental_price = float(request.POST.get('rental_price'))
        #is_available = bool(request.POST.get('is_available'))
        is_available = 'is_available' in request.POST

        representative = Representative.objects.first()


        car = Car.objects.create(
            model=model,
            brand=brand,
            year=year,
            rental_price=rental_price,
            is_available=is_available,
            representative=representative,
        )
        car.save()
        return redirect('dashboard')  # Po dodaniu przekierowujemy do dashboardu

    return render(request, 'app/add_car.html')


@login_required
def rent_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():

            start_date= form.cleaned_data['start_date']
            # end_date = str(form.cleaned_data['end_date'])
            end_date  = end_date = form.cleaned_data['end_date']
            days = (end_date - start_date).days
            total_cost = float(car.rental_price * days)

            # Dane do podsumowania
            request.session['rental_data'] = {
                'car_id': car.id,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_cost': total_cost,
            }

            return redirect('reservation_summary', car_id=car.id)

    else:
        form = RentalForm()

    return render(request, 'app/rent_car.html', {'form': form, 'car': car})


def availability_calendar(request):

    today = timezone.now().date()


    cars = Car.objects.all()


    rentals = Rental.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='active'
    )


    available_cars = [car for car in cars if not any(rental.car == car for rental in rentals)]


    return render(request, 'app/availability_calendar.html', {
        'available_cars': available_cars,
        'today': today,
    })

@login_required
def rental_confirmation(request, rental_id):
    rental = Rental.objects.get(id=rental_id)
    return render(request, 'app/rental_confirmation.html', {'rental': rental})



@login_required
def reservation_summary(request, car_id):
    rental_data = request.session.get('rental_data', None)

    if rental_data is None:
        return redirect('rent_car', car_id=car_id)

    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        accept_terms = request.POST.get('accept_terms')

        if accept_terms != 'on':
            messages.error(request, "Musisz zaakceptować warunki wypożyczenia!")
            return redirect('reservation_summary', car_id=car_id)

        # Tworzenie nowego wypożyczenia
        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method=payment_method,
            status='active',
            payment_status='pending'
        )
        rental.save()

        car.is_available = False
        car.save()

        del request.session['rental_data']

        return redirect('rentals')
    return render(request, 'app/reservation_summary.html', {'car': car, 'rental_data': rental_data})


def terms_conditions(request):
    car_id = request.GET.get('car_id')  # Odczytanie car_id z parametrów GET
    car = get_object_or_404(Car, id=car_id) if car_id else None  # Pobranie samochodu na podstawie car_id

    return render(request, 'app/terms_conditions.html', {'car': car})


@login_required
def reservation_summary(request, car_id):
    rental_data = request.session.get('rental_data')

    if not rental_data:
        return redirect('rent_car', car_id=car_id)

    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, "Wybierz metodę płatności!")
            return redirect('reservation_summary', car_id=car_id)

        # Dane płatności
        rental_data['payment_method'] = payment_method
        request.session['rental_data'] = rental_data

        if payment_method == 'credit_card':
            return redirect('payment_card', car_id=car_id)
        elif payment_method == 'bank_transfer':
            return redirect('payment_bank', car_id=car_id)
        elif payment_method == 'paypal':
            return redirect('payment_paypal', car_id=car_id)
        elif payment_method == 'cash':
            return redirect('payment_cash', car_id=car_id)

    return render(request, 'app/reservation_summary.html', {
        'car': car,
        'rental_data': rental_data,
    })


@login_required
def payment_view(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    if request.method == 'POST':
        # Logika przetwarzania płatności
        rental.payment_status = 'paid'
        rental.save()

        return redirect('rentals')  # Przekierowanie do listy rezerwacji

    return render(request, 'app/payment.html', {'rental': rental})


@login_required
def payment_card(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

    if not rental_data:
        messages.error(request, "Brak danych rezerwacji.")
        return redirect('rent_car', car_id=car_id)

    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_holder = request.POST.get('card_holder')
        expiry_date = request.POST.get('expiry_date')
        csv_code = request.POST.get('csv_code')

        if not all([card_number, card_holder, expiry_date, csv_code]):
            messages.error(request, "Wprowadź wszystkie wymagane dane karty!")
            return redirect('payment_card', car_id=car_id)


        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method='credit_card',
            payment_status='completed',
        )

        car.is_available = False
        car.save()
        del request.session['rental_data']

        return redirect('payment_success')

    return render(request, 'app/payment_card.html', {'car': car, 'rental_data': rental_data})

@login_required
def payment_bank(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

    if not rental_data:
        messages.error(request, "Brak danych rezerwacji.")
        return redirect('rent_car', car_id=car_id)

    if request.method == 'POST':
        # Zapisanie wypożyczenia
        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method='bank_transfer',
            payment_status='pending',
        )

        car.is_available = False
        car.save()
        del request.session['rental_data']

        return redirect('payment_success')

    return render(request, 'app/payment_bank.html', {
        'car': car,
        'rental_data': rental_data,
        'bank_account': '1111111111111111',
        'owner_name': 'Piotr Wojtalewicz',
        'company_name': 'Car_rental_PW',
    })







@login_required
def payment_paypal(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

    if not rental_data:
        messages.error(request, "Brak danych rezerwacji.")
        return redirect('rent_car', car_id=car_id)

    if request.method == 'POST':
        # Zapisanie wypożyczenia
        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method='paypal',
            payment_status='completed',
        )

        car.is_available = False
        car.save()
        del request.session['rental_data']

        return redirect('payment_success')

    return render(request, 'app/payment_paypal.html', {'car': car, 'rental_data': rental_data})



@login_required
def payment_cash(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

    if not rental_data:
        messages.error(request, "Brak danych rezerwacji.")
        return redirect('rent_car', car_id=car_id)

    if request.method == 'POST':

        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method='cash',
            payment_status='pending',
        )

        car.is_available = False
        car.save()
        del request.session['rental_data']

        return redirect('payment_success')

    return render(request, 'app/payment_cash.html', {'car': car, 'rental_data': rental_data})




from decimal import Decimal

@login_required
def extend_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    if request.method == 'POST':
        extra_days = int(request.POST.get('extra_days', 0))
        payment_method = request.POST.get('payment_method')

        if extra_days <= 0 or not payment_method:
            messages.error(request, "Proszę wybrać poprawną liczbę dni i metodę płatności.")
            return redirect('extend_rental', rental_id=rental_id)


        new_end_date = rental.end_date + timedelta(days=extra_days)
        additional_cost = Decimal(extra_days) * rental.car.rental_price + Decimal('20')


        request.session['extend_rental_data'] = {
            'rental_id': rental.id,
            'extra_days': extra_days,
            'new_end_date': new_end_date.strftime('%Y-%m-%d'),
            'additional_cost': str(additional_cost),
            'payment_method': payment_method,
        }


        if payment_method == 'credit_card':
            return redirect('payment_card', car_id=rental.car.id)
        elif payment_method == 'bank_transfer':
            return redirect('payment_bank', car_id=rental.car.id)
        elif payment_method == 'paypal':
            return redirect('payment_paypal', car_id=rental.car.id)

    return render(request, 'app/extend_rental.html', {'rental': rental})

@login_required
def payment_success(request):
    messages.success(request, "Płatność zakończona sukcesem!")
    return render(request, 'app/payment_success.html')