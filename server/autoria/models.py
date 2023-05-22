import datetime

from django.db import models
from bulk_update_or_create import BulkUpdateOrCreateQuerySet

# Create your models here.


class Task(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    time_created = models.DateTimeField(default=datetime.datetime.now)


class Cars(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    id = models.AutoField(primary_key=True, db_index=True)
    url = models.CharField(null=False, unique=True)
    profile_name = models.CharField(null=True)
    phone_number = models.CharField(null=False)
    title = models.CharField(null=False)
    price = models.IntegerField(null=False)
    mileage = models.IntegerField()
    image_url = models.CharField(null=True)
    image_count = models.IntegerField(null=True)
    car_number = models.CharField(null=True)
    datetime_crawling = models.DateTimeField(default=datetime.datetime.now)