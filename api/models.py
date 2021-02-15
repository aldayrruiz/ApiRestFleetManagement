import uuid
from django.db import models
from django.db.models import UniqueConstraint
from .utils import IncidentType, UserType


class VehicleType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)

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
    type = models.ForeignKey(VehicleType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Vehicle'


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.CharField(
        max_length=1,
        choices=UserType.choices,
        default=UserType.USUARIO
    )

    # Email, phone?
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

    def __str__(self):
        return self.fullname

    class Meta:
        db_table = 'User'


class AllowedTypes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)

    class Meta:
        db_table = 'AllowedTypes'
        constraints = [
            UniqueConstraint(fields=['user', 'type'], name='constraint_user_type')
        ]


# It is intended to be a history of positions
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    datetime = models.DateTimeField(auto_now_add=True)

    # GPS Position
    latitude = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Track'


class Incident(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
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
        return '%s - %s - %s' % (self.type, self.user.fullname, self.vehicle.name)


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Reservation'
