import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from applications.diets.models.type import DietType
from applications.reservations.models import Reservation
from applications.tenants.models import Tenant


class DietCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(Reservation, related_name='diet_collection', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='diet_collections', on_delete=models.CASCADE)
    # Start & end are fields completed by the user. They are used to know if entire day or half day diet is needed.
    start = models.DateTimeField()
    end = models.DateTimeField()
    completed = models.BooleanField(default=False)
    modified = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DietCollection'


class Diet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='diets', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=DietType.choices, default=DietType.Otros)
    liters = models.IntegerField(default=-1, blank=True)  # Si la dieta es de tipo gasolina, se debe registrar el número de litros
    amount = models.IntegerField(default=0)  # Amount: El importe de la dieta
    description = models.TextField(default='', blank=True)
    collection = models.ForeignKey(DietCollection, related_name='diets', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='diets', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Diet'


class DietPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diet = models.ForeignKey(Diet, related_name='photos', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='diet_photos', on_delete=models.CASCADE)
    photo = models.ImageField(default='diet/none.png', upload_to='diets')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DietPhoto'


@receiver(models.signals.post_delete, sender=DietPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `DietPhoto` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
