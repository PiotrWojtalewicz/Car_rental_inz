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
                return redirect('dashboard')  # Przekierowanie na stronę z listą samochodów (lub inną stronę)
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
    # Placeholder dla historii wypożyczeń
    rentals = []  # W przyszłości dodamy rzeczywiste dane wypożyczeń użytkownika
    return render(request, 'app/rental_history.html', {'rentals': rentals})

def available_cars(request):
    # Pobierz dostępne samochody
    cars = Car.objects.filter(is_available=True)  # Zakładając, że pole `is_available` wskazuje dostępność
    return render(request, 'app/available_cars.html', {'cars': cars})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Przekierowanie po zapisaniu
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'app/edit_profile.html', {'form': form})

@login_required
def rental_history(request):
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'app/rental_history.html', {'rentals': rentals})

def user_rentals(request):
    # Pobieramy wszystkie wypożyczenia danego użytkownika
    rentals = Rental.objects.filter(user=request.user)

    # Przekazujemy zmienną rentals do szablonu
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

        # Możesz dodać reprezentanta lub ustawić go na None
        representative = Representative.objects.first()  # Ustaw jakiegoś reprezentanta lub None

        # Tworzymy nowy samochód
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

# @login_required
# def rent_car(request, car_id):
#     car = Car.objects.get(id=car_id)
#
#     # Tworzymy wypożyczenie
#     rental = Rental.objects.create(
#         car=car,
#         user=request.user,
#         start_date=timezone.now().date(),
#         end_date=timezone.now().date() + timedelta(days=7),  # Na przykład 7 dni
#         total_cost=car.rental_price * 7,  # Koszt wypożyczenia na 7 dni
#     )
#
#     # Zmiana dostępności samochodu na niedostępny
#     car.is_available = False
#     car.save()
#
#     return redirect('rentals')

# def rent_car(request, car_id):
#     car = Car.objects.get(id=car_id)
#
#     if request.method == 'POST':
#         form = RentalForm(request.POST)
#         if form.is_valid():
#             # Pobieramy dane z formularza
#
#             start_date = form.cleaned_data['start_date']
#             end_date = form.cleaned_data['end_date']
#             total_cost = car.rental_price * (end_date - start_date).days  # Obliczamy koszt na podstawie dat
#
#             # Tworzymy nowe wypożyczenie
#             rental = Rental.objects.create(
#                 car=car,
#                 user=request.user,
#                 start_date=start_date,
#                 end_date=end_date,
#                 total_cost=total_cost,
#             )
#
#             # Zmieniamy dostępność samochodu na niedostępny
#             car.is_available = False
#             car.save()
#
#             return redirect('rentals')  # Przekierowanie do strony z listą wypożyczeń
#     else:
#         form = RentalForm()
#
#     return render(request, 'app/rent_car.html', {'form': form, 'car': car})
# @login_required
# def rent_car(request, car_id):
#     car = get_object_or_404(Car, id=car_id)
#
#     if request.method == 'POST':
#         form = RentalForm(request.POST)
#         if form.is_valid():
#             # Utwórz obiekt rezerwacji, ale go nie zapisuj jeszcze
#             rental = form.save(commit=False)
#             rental.car = car
#             rental.user = request.user
#
#             # Oblicz koszt rezerwacji
#             start_date = rental.start_date
#             end_date = rental.end_date
#             rental_duration = (end_date - start_date).days
#             total_cost = car.rental_price * rental_duration
#             rental.total_cost = total_cost
#
#             # Przekierowanie do strony podsumowania rezerwacji
#             request.session['rental_data'] = {
#                 'car_id': car.id,
#                 'start_date': start_date,
#                 'end_date': end_date,
#                 'total_cost': total_cost
#             }
#
#             return redirect('reservation_summary')  # Przekierowanie do podsumowania
#     else:
#         form = RentalForm()
#
#     return render(request, 'rent_car.html', {'form': form, 'car': car})

@login_required
def rent_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            # Tworzymy wypożyczenie na podstawie danych z formularza
            rental = form.save(commit=False)
            rental.user = request.user
            rental.car = car
            rental.total_cost = car.rental_price * (rental.end_date - rental.start_date).days  # Koszt wypożyczenia
            rental.save()

            # Zmiana dostępności samochodu na niedostępny
            car.is_available = False
            car.save()

            return redirect('rentals')  # Przekierowanie do strony z listą wypożyczeń
            # return redirect('reservation_summary', car_id=car.id, start_date=rental.start_date,
                            # end_date=rental.end_date)
    else:
        form = RentalForm()

    return render(request, 'app/rent_car.html', {'form': form, 'car': car})



# @login_required
# def car_rental(request, car_id):
#     car = Car.objects.get(id=car_id)
#     form = RentalForm(request.POST or None)
#
#     if request.method == "POST" and form.is_valid():
#         # Sprawdzamy, czy samochód jest dostępny w wybranym okresie
#         start_date = form.cleaned_data['start_date']
#         end_date = form.cleaned_data['end_date']
#
#         conflicting_rentals = Rental.objects.filter(
#             car=car,
#             start_date__lt=end_date,
#             end_date__gt=start_date,
#             status='active'
#         )
#
#         if conflicting_rentals.exists():
#             form.add_error(None, "Samochód jest niedostępny w wybranym okresie.")
#         else:
#             rental = form.save(commit=False)
#             rental.user = request.user
#             rental.car = car
#             rental.status = 'active'
#             rental.total_cost = rental.calculate_total_cost()
#             car.is_available = False  # Samochód nie jest dostępny
#             car.save()
#             rental.save()
#             return redirect('rental_confirmation', rental_id=rental.id)
#
#     return render(request, 'app/car_rental.html', {
#         'car': car,
#         'form': form
#     })
def availability_calendar(request):
    # Pobranie dzisiejszej daty
    today = timezone.now().date()

    # Pobranie wszystkich samochodów
    cars = Car.objects.all()

    # Wyszukiwanie wypożyczeń w wybranym dniu
    rentals = Rental.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='active'
    )

    # Lista samochodów, które są dostępne w danym dniu
    available_cars = [car for car in cars if not any(rental.car == car for rental in rentals)]

    # Renderowanie szablonu
    return render(request, 'app/availability_calendar.html', {
        'available_cars': available_cars,
        'today': today,
    })

@login_required
def rental_confirmation(request, rental_id):
    rental = Rental.objects.get(id=rental_id)
    return render(request, 'app/rental_confirmation.html', {'rental': rental})


@login_required
def reservation_summary(request):
    rental_data = request.session.get('rental_data', None)

    if rental_data is None:
        return redirect('rent_car')  # Jeśli brak danych, wróć do formularza

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        accept_terms = request.POST.get('accept_terms')

        if accept_terms != 'on':
            messages.error(request, "Musisz zaakceptować warunki wypożyczenia!")
            return redirect('reservation_summary')  # Przekierowanie z komunikatem o błędzie

        # Utwórz rezerwację na podstawie danych z sesji
        car = get_object_or_404(Car, id=rental_data['car_id'])
        rental = Rental.objects.create(
            car=car,
            user=request.user,
            start_date=rental_data['start_date'],
            end_date=rental_data['end_date'],
            total_cost=rental_data['total_cost'],
            payment_method=payment_method,
        )

        # Zmiana dostępności samochodu na niedostępny
        car.is_available = False
        car.save()

        # Usuń dane z sesji
        del request.session['rental_data']

        return redirect('rentals')

# def terms_conditions(request):
#     return render(request, 'app/terms_conditions.html')
def terms_conditions(request):
    car_id = request.GET.get('car_id')  # Odczytanie car_id z parametrów GET
    car = get_object_or_404(Car, id=car_id) if car_id else None  # Pobranie samochodu na podstawie car_id

    return render(request, 'app/terms_conditions.html', {'car': car})

@login_required
def reservation_summary(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        # Sprawdź, czy formularz płatności jest poprawny
        payment_method = request.POST.get('payment_method')

        # Tu możesz dodać logikę do przetwarzania płatności w zależności od wybranej metody
        # Na razie tylko wyświetlimy podsumowanie, ale możesz rozszerzyć to o integrację z API płatności

        return render(request, 'app/payment_success.html', {'car': car, 'payment_method': payment_method})

    # Wypełniamy dane o rezerwacji
    rental_start_date = request.GET.get('start_date')
    rental_end_date = request.GET.get('end_date')
    rental_days = (rental_end_date - rental_start_date).days
    total_cost = car.rental_price * rental_days

    return render(request, 'app/reservation_summary.html', {
        'car': car,
        'rental_start_date': rental_start_date,
        'rental_end_date': rental_end_date,
        'rental_days': rental_days,
        'total_cost': total_cost
    })