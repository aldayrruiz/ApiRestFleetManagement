import uuid

from django.db import models


# TODO: Implements a way to store the vehicle's time of user during a reservation.
#       Solution: Adds a integer field (minutes) to count each time a new vehicle's track is added.
#       Problems: I do not know how gps sends tracks (intervals).


# Create your models here.
class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    model = models.CharField(max_length=50)
    # Brand: Marca de coche
    brand = models.CharField(max_length=50)
    # Número de matricula
    number_plate = models.CharField(max_length=50, unique=True)
    date_stored = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.brand

    class Meta:
        db_table = 'Vehicle'
