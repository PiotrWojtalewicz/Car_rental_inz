from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rental

@receiver(post_save, sender=Rental)
def update_rental_status(sender, instance, **kwargs):
    instance.update_status()
