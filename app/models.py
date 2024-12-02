from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
