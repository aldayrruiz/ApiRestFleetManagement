import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

from applications.tenants.models.tenant import Tenant
from applications.users.models.role import Role
from applications.vehicles.models.vehicle import Vehicle


class MyUserManager(BaseUserManager):
    def create_user(self, email, fullname, tenant, password=None):
        try:
            tenant = Tenant.objects.get(id=tenant)
        except ValidationError:
            raise ValueError('Tenant UUID not valid. Use "python manage.py showtenants" to see ids')
        except Tenant.DoesNotExist:
            raise ValueError('Tenant does not exists. Use "python manage.py showtenants" to see ids')

        if not email:
            raise ValueError('Users must have an email address.')
        if not fullname:
            raise ValueError('Users must have a fullname.')

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname,
        )
        user.tenant = tenant
        user.role = Role.USER
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, tenant, password=None):

        user = self.create_user(
            email,
            fullname=fullname,
            tenant=tenant,
            password=password,
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
    fullname = models.CharField(verbose_name='fullname', max_length=70)
    tenant = models.ForeignKey(Tenant, related_name='users', on_delete=models.CASCADE)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_interventor = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    ble_user_id = models.CharField(max_length=12, default='', blank=True)

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
    REQUIRED_FIELDS = ['fullname', 'tenant']

    objects = MyUserManager()

    def __str__(self):
        return '{} ({})'.format(self.fullname, self.email)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'User'
