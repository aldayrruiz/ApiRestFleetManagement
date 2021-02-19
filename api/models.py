import uuid
from django.db import models
from django.db.models import UniqueConstraint
from .utils import IncidentType
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Flota: Valladolid, etc.
class Fleet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Fleet'


class VehicleType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'VehicleType'


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    # Useful to know when vehicle pass their days to use. Column days_to_use could be decremental too.
    date_stored = models.DateField(auto_now_add=True)
    # Vehicle's days should be used after it was stored (date_stored)
    days_to_use = models.IntegerField()
    # If a vehicle is available depending of maintenance, etc. Available field is not related with reservation.
    available = models.BooleanField(default=True)
    # Type: 4x4, bus, moto, etc
    type = models.ForeignKey(VehicleType, related_name='vehicles', null=True, on_delete=models.SET_NULL)
    # Not to delete vehicle if fleet is deleted.
    fleet = models.ForeignKey(Fleet, related_name='vehicles', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Vehicle'


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    allowed_types = models.ManyToManyField(
        VehicleType,
        through='AllowedTypes',
        through_fields=('user', 'type'),
        related_name='allowed_types'
    )

    incidents = models.ManyToManyField(
        Vehicle,
        through='Incident',
        through_fields=('user', 'vehicle'),
        related_name='incidents'
    )

    fleet = models.ForeignKey(Fleet, related_name='users', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.username


class AllowedTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)

    class Meta:
        db_table = 'AllowedTypes'
        constraints = [
            UniqueConstraint(fields=['user', 'type'], name='constraint_user_type')
        ]

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.type)


# It is intended to be a history of positions
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    datetime = models.DateTimeField(auto_now_add=True)

    # GPS Position
    latitude = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)
    altitude = models.DecimalField(max_digits=13, decimal_places=10)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Track'

    def __str__(self):
        return '{0} ({1:.5g}{2:.5g}}{3:.5g}})'.format(self.vehicle.name, self.latitude, self.longitude, self.altitude)


class Incident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    # This position will be the last position of the vehicle when an incident is reported.
    position = models.OneToOneField(Track, null=True, on_delete=models.SET_NULL)
    datetime = models.DateTimeField(auto_now_add=True)

    type = models.CharField(
        max_length=2,
        choices=IncidentType.choices,
        default=IncidentType.OTRO
    )

    description = models.CharField(max_length=255)
    solved = models.BooleanField(default=False)

    class Meta:
        db_table = 'Incident'

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.type, self.user, self.vehicle.name)


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_stored = models.DateField(auto_now_add=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reservations', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='reservations', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Reservation'

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.user, self.vehicle.name, self.start)
