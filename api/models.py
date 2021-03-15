import uuid
from django.db import models
from django.db.models import UniqueConstraint
from .utils import IncidentType
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


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


# TODO: Implements a way to store the vehicle's time of user during a reservation.
#       Solution: Adds a integer field (minutes) to count each time a new vehicle's track is added.
#       Problems: I do not know how gps sends tracks (intervals).

class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    # Useful to know when vehicle pass their days to use. Column days_to_use could be decremental too.
    date_stored = models.DateField(auto_now_add=True)
    # Type: 4x4, bus, moto, etc
    type = models.ForeignKey(VehicleType, related_name='vehicles', null=True, on_delete=models.SET_NULL)
    # Not to delete vehicle if fleet is deleted.
    fleet = models.ForeignKey(Fleet, related_name='vehicles', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Vehicle'


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    username = models.CharField(verbose_name='username', max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


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
        ordering = ['start']

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.user, self.vehicle.name, self.start)


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_stored = models.DateField(auto_now_add=True)
    description = models.TextField()
    reservation = models.ForeignKey(Reservation, related_name='tickets', on_delete=models.CASCADE)

    # Person who request other person to cancel his reservation.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Ticket'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Token is generated automatically when a user is created.
    """
    if created:
        Token.objects.create(user=instance)
