import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from applications.vehicles.models import Vehicle


class Role(models.TextChoices):
    """
    Admin has access to mobile app and admin web site.
    User has access only to mobile app.
    """
    ADMIN = 'ADMIN', _('Admin'),
    USER = 'USER', _('User')


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None):
        if not email:
            raise ValueError('Users must have an email address.')
        if not name:
            raise ValueError('Users must have a name.')
        if not surname:
            raise ValueError('Users must have a surname.')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname
        )
        user.role = Role.USER
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None):
        user = self.create_user(
            email,
            password=password,
            name=name,
            surname=surname
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.role = Role.ADMIN
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    name = models.CharField(verbose_name='name', max_length=50)
    surname = models.CharField(verbose_name='surname', max_length=50)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)

    allowed_vehicles = models.ManyToManyField(
        Vehicle,
        through='allowed_vehicles.AllowedVehicles',
        through_fields=('user', 'vehicle'),
        related_name='allowed_vehicles'
    )

    role = models.CharField(
        max_length=11,
        choices=Role.choices,
        default=Role.USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = MyUserManager()

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.surname, self.email)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'User'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Token is generated automatically when a user is created.
    """
    if created:
        Token.objects.create(user=instance)
