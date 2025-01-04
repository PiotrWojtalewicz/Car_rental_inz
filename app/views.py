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

# @login_required
# def rental_history(request):
#     # Placeholder dla historii wypożyczeń
#     rentals = []  # W przyszłości dodamy rzeczywiste dane wypożyczeń użytkownika
#     return render(request, 'app/rental_history.html', {'rentals': rentals})
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

# @login_required
# def rental_history(request):
#     rentals = Rental.objects.filter(user=request.user)
#     return render(request, 'app/rental_history.html', {'rentals': rentals})
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

# def user_rentals(request):
#     # Pobieramy wszystkie wypożyczenia danego użytkownika
#     rentals = Rental.objects.filter(user=request.user)
#
#     # Przekazujemy zmienną rentals do szablonu
#     return render(request, 'app/rentals.html', {'rentals': rentals})

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

# @login_required
# def rent_car(request, car_id):
#     car = get_object_or_404(Car, id=car_id)
#
#     if request.method == 'POST':
#         form = RentalForm(request.POST)
#         if form.is_valid():
#             # Tworzymy wypożyczenie na podstawie danych z formularza
#             rental = form.save(commit=False)
#             rental.user = request.user
#             rental.car = car
#             rental.total_cost = car.rental_price * (rental.end_date - rental.start_date).days  # Koszt wypożyczenia
#             rental.save()
#
#             # Zmiana dostępności samochodu na niedostępny
#             car.is_available = False
#             car.save()
#
#             return redirect('rentals')  # Przekierowanie do strony z listą wypożyczeń
#             # return redirect('reservation_summary', car_id=car.id, start_date=rental.start_date,
#                             # end_date=rental.end_date)
#     else:
#         form = RentalForm()
#
#     return render(request, 'app/rent_car.html', {'form': form, 'car': car})

@login_required
def rent_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            # Dane z formularza
            # start_date = str(form.cleaned_data['start_date'])
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

# @login_required
# def reservation_summary(request, car_id):
#     car = get_object_or_404(Car, id=car_id)
#
#     if request.method == 'POST':
#         # Sprawdź, czy formularz płatności jest poprawny
#         payment_method = request.POST.get('payment_method')
#
#         # Tu możesz dodać logikę do przetwarzania płatności w zależności od wybranej metody
#         # Na razie tylko wyświetlimy podsumowanie, ale możesz rozszerzyć to o integrację z API płatności
#
#         return render(request, 'app/payment_success.html', {'car': car, 'payment_method': payment_method})
#
#     # Wypełniamy dane o rezerwacji
#     rental_start_date = request.GET.get('start_date')
#     rental_end_date = request.GET.get('end_date')
#     rental_days = (rental_end_date - rental_start_date).days
#     total_cost = car.rental_price * rental_days
#
#     return render(request, 'app/reservation_summary.html', {
#         'car': car,
#         'rental_start_date': rental_start_date,
#         'rental_end_date': rental_end_date,
#         'rental_days': rental_days,
#         'total_cost': total_cost
#     })
# @login_required
# def reservation_summary(request, car_id):
#     rental_data = request.session.get('rental_data')
#
#     if not rental_data:
#         return redirect('rent_car', car_id=car_id)
#
#     car = get_object_or_404(Car, id=car_id)
#
#     if request.method == 'POST':
#         payment_method = request.POST.get('payment_method')
#
#         if not payment_method:
#             messages.error(request, "Wybierz metodę płatności!")
#             return redirect('reservation_summary', car_id=car_id)
#
#         # Dane płatności
#         rental_data['payment_method'] = payment_method
#         request.session['rental_data'] = rental_data
#
#         return redirect('payment_view', rental_id=rental_data['rental_id'])
#
#     return render(request, 'app/reservation_summary.html', {
#         'car': car,
#         'rental_data': rental_data,
#     })
# @login_required
# def reservation_summary(request, car_id):
#     rental_data = request.session.get('rental_data')
#
#     if not rental_data:
#         return redirect('rent_car', car_id=car_id)
#
#     car = get_object_or_404(Car, id=car_id)
#
#     # Oblicz liczbę dni
#     rental_start_date = datetime.strptime(rental_data['start_date'], '%Y-%m-%d').date()
#     rental_end_date = datetime.strptime(rental_data['end_date'], '%Y-%m-%d').date()
#     rental_days = (rental_end_date - rental_start_date).days
#
#     if request.method == 'POST':
#         payment_method = request.POST.get('payment_method')
#
#         if not payment_method:
#             messages.error(request, "Wybierz metodę płatności!")
#             return redirect('reservation_summary', car_id=car_id)
#
#         # Dane płatności
#         rental_data['payment_method'] = payment_method
#         request.session['rental_data'] = rental_data
#
#         return redirect('payment_view', rental_id=rental_data['rental_id'])
#
#     # Przekazanie rental_days do kontekstu
#     return render(request, 'app/reservation_summary.html', {
#         'car': car,
#         'rental_data': rental_data,
#         'rental_days': rental_days,
#     })

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

    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_holder = request.POST.get('card_holder')
        expiry_date = request.POST.get('expiry_date')
        csv_code = request.POST.get('csv_code')

        # Walidacja danych karty (opcjonalnie)
        if not card_number or not card_holder or not expiry_date or not csv_code:
            messages.error(request, "Wprowadź wszystkie wymagane dane karty!")
            return redirect('payment_card', car_id=car_id)

        # Logika płatności kartą (np. z użyciem API płatności)
        return redirect('payment_success')

    return render(request, 'app/payment_card.html', {'car': car, 'rental_data': rental_data})
@login_required
def payment_bank(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

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

    # Tutaj możesz dodać integrację z API PayPal
    return render(request, 'app/payment_paypal.html', {'car': car, 'rental_data': rental_data})

@login_required
def payment_cash(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    rental_data = request.session.get('rental_data')

    # Możesz tutaj dodać wysyłkę potwierdzenia mailowego (opcjonalnie)
    return render(request, 'app/payment_cash.html', {'car': car})

# @login_required
# def extend_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id, user=request.user)
#
#     if request.method == "POST":
#         additional_days = int(request.POST.get("additional_days", 0))
#         new_end_date = rental.end_date + timezone.timedelta(days=additional_days)
#         additional_cost = (rental.car.rental_price * additional_days) + 20  # 20 zł opłaty serwisowej
#
#         rental.end_date = new_end_date
#         rental.total_cost += additional_cost
#         rental.save()
#
#         return redirect("rentals")
#         messages.success(request, "Pomyślnie przedłużono wypożyczenie samochodu!")
#     return render(request, "app/extend_rental.html", {
#         "rental": rental,
#         "car": rental.car,
#         "additional_cost_per_day": rental.car.rental_price,
#         "service_fee": 20,
#     })
# @login_required
# def extend_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id)
#
#     if request.method == 'POST':
#         extra_days = int(request.POST.get('extra_days', 0))
#         payment_method = request.POST.get('payment_method')
#
#         if extra_days <= 0 or not payment_method:
#             messages.error(request, "Proszę wybrać poprawną liczbę dni i metodę płatności.")
#             return redirect('extend_rental', rental_id=rental_id)
#
#         # Oblicz nową datę zakończenia i koszt
#         new_end_date = rental.end_date + timedelta(days=extra_days)
#         additional_cost = rental.car.rental_price * extra_days + 20  # 20 PLN opłata serwisowa
#
#         # Przechowaj dane w sesji
#         request.session['extend_rental_data'] = {
#             'rental_id': rental.id,
#             'extra_days': extra_days,
#             'new_end_date': new_end_date.strftime('%Y-%m-%d'),
#             'additional_cost': additional_cost,
#             'payment_method': payment_method,
#         }
#
#         # Przekierowanie na odpowiednią stronę płatności
#         if payment_method == 'credit_card':
#             return redirect('payment_card', car_id=rental.car.id)
#         elif payment_method == 'bank_transfer':
#             return redirect('payment_bank', car_id=rental.car.id)
#         elif payment_method == 'paypal':
#             return redirect('payment_paypal', car_id=rental.car.id)
#
#     return render(request, 'app/extend_rental.html', {'rental': rental})

# @login_required
# def extend_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id)
#
#     if request.method == 'POST':
#         try:
#             extra_days = int(request.POST.get('extra_days', 0))
#         except ValueError:
#             messages.error(request, "Podaj poprawną liczbę dni.")
#             return redirect('extend_rental', rental_id=rental_id)
#         messages.success(request, "Pomyślnie przedłużono wypożyczenie samochodu!")
#         payment_method = request.POST.get('payment_method')
#
#         if extra_days <= 0 or not payment_method:
#             messages.error(request, "Proszę wybrać poprawną liczbę dni i metodę płatności.")
#             return redirect('extend_rental', rental_id=rental_id)
#
#         # Oblicz nową datę zakończenia i koszt
#         new_end_date = rental.end_date + timedelta(days=extra_days)
#         additional_cost = float(rental.car.rental_price * extra_days) + 20.0  # Konwersja Decimal na float + opłata serwisowa
#
#         # Przechowaj dane w sesji
#         request.session['extend_rental_data'] = {
#             'rental_id': rental.id,
#             'extra_days': extra_days,
#             'new_end_date': new_end_date.strftime('%Y-%m-%d'),
#             'additional_cost': additional_cost,  # Przechowywanie jako float
#             'payment_method': payment_method,
#         }
#
#         # Przekierowanie na odpowiednią stronę płatności
#         if payment_method == 'credit_card':
#             return redirect('payment_card', car_id=rental.car.id)
#         elif payment_method == 'bank_transfer':
#             return redirect('payment_bank', car_id=rental.car.id)
#         elif payment_method == 'paypal':
#             return redirect('payment_paypal', car_id=rental.car.id)
#
#     return render(request, 'app/extend_rental.html', {'rental': rental})

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

        # Oblicz nową datę zakończenia i koszt
        new_end_date = rental.end_date + timedelta(days=extra_days)
        additional_cost = Decimal(extra_days) * rental.car.rental_price + Decimal('20')  # 20 PLN opłata serwisowa

        # Przechowaj dane w sesji
        request.session['extend_rental_data'] = {
            'rental_id': rental.id,
            'extra_days': extra_days,
            'new_end_date': new_end_date.strftime('%Y-%m-%d'),
            'additional_cost': str(additional_cost),  # Konwersja na string, aby uniknąć problemów z serializacją
            'payment_method': payment_method,
        }

        # Przekierowanie na odpowiednią stronę płatności
        if payment_method == 'credit_card':
            return redirect('payment_card', car_id=rental.car.id)
        elif payment_method == 'bank_transfer':
            return redirect('payment_bank', car_id=rental.car.id)
        elif payment_method == 'paypal':
            return redirect('payment_paypal', car_id=rental.car.id)

    return render(request, 'app/extend_rental.html', {'rental': rental})

def payment_success(request):
    return render(request,'app/payment_success')