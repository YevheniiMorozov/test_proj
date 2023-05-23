import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import caches

from autoria.models import Cars


@receiver(post_save, sender=Cars)
def add_car_items_to_spreadsheets_cache(sender, **kwargs):
    cache = caches["sheets"]
    data = list(Cars.objects.values_list('url', 'profile_name', 'phone_number', 'title', 'price', 'mileage', 'image_url'))
    cache.set(uuid.uuid4(), data, None)

