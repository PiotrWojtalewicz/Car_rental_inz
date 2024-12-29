from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
class Representative(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Car(models.Model):
    BRANDS = (
        ('BMW', 'BMW'),
        ('AUDI', 'Audi'),
        ('MERCEDES', 'Mercedes'),
        ('TOYOTA', 'Toyota'),
        ('HONDA', 'Honda'),  # Dodano przecinek
        ('FORD', 'Ford'),
    )

    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=20, choices=BRANDS)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2024)])
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    representative = models.ForeignKey(Representative, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    def get_fields(self):
        return [(field.verbose_name, field.value_from_object(self))
                if field.verbose_name != 'representative'
                else (field.verbose_name,
                      Representative.objects.get(pk=field.value_from_object(self)).name)
                for field in self.__class__._meta.fields]


# class Representative(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name


class Car(models.Model):
    BRANDS = (
        ('BMW', 'BMW'),
        ('AUDI', 'Audi'),
        ('MERCEDES', 'Mercedes'),
        ('TOYOTA', 'Toyota'),
        ('HONDA', 'Honda'),  # Dodano przecinek
        ('FORD', 'Ford'),
    )

    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=20, choices=BRANDS)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2024)])
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    representative = models.ForeignKey(Representative, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    def get_fields(self):
        return [(field.verbose_name, field.value_from_object(self))
                if field.verbose_name != 'representative'
                else (field.verbose_name,
                      Representative.objects.get(pk=field.value_from_object(self)).name)
                for field in self.__class__._meta.fields]

    def is_available_on(self, start_date, end_date):
        """
        Sprawdza, czy samochód jest dostępny w danym okresie.
        """
        # Sprawdzamy, czy istnieje wypożyczenie tego samochodu w podanym okresie.
        conflicting_rentals = Rental.objects.filter(
            car=self,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='active'
        )
        return not conflicting_rentals.exists()

    def update_availability(self):
        """
        Zmienia dostępność samochodu na 'True', jeśli nie ma aktywnych wypożyczeń,
        lub 'False', jeśli samochód jest wypożyczony.
        """
        if self.is_available_on(timezone.now().date(), timezone.now().date()):
            self.is_available = True
        else:
            self.is_available = False
        self.save()

# Dodajemy model wypożyczenia

class Rental(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')],
                                      default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.car.brand} {self.car.model} ({self.start_date} to {self.end_date})"

    def calculate_total_cost(self):
        # Funkcja do obliczania całkowitego kosztu na podstawie dni wynajmu i ceny za dzień
        rental_duration = (self.end_date - self.start_date).days
        return rental_duration * self.car.rental_price

    def save(self, *args, **kwargs):
        # Obliczamy koszt przed zapisaniem modelu
        if not self.total_cost:
            self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def is_conflicting(self):
        """
        Sprawdza, czy istnieje jakiekolwiek inne wypożyczenie tego samego samochodu w tym samym czasie.
        """
        conflicting_rentals = Rental.objects.filter(
            car=self.car,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            status='active'
        )
        return conflicting_rentals.exists()