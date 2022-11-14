import uuid

from django.core.validators import MinLengthValidator
from django.db import models

from applications.insurance_companies.models.insurance_company import InsuranceCompany
from applications.tenants.models.tenant import Tenant
from applications.traccar.models.device import Device
from applications.vehicles.models import VehicleType
from applications.vehicles.models.fuel import Fuel

# In Spain vehicle's number plates have 7 characters, except for motorbikes
MIN_LENGTH_NUMBER_PLATE = 7
MAX_LENGTH_NUMBER_PLATE = 8


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    model = models.CharField(max_length=50)

    brand = models.CharField(max_length=20)

    number_plate = models.CharField(
        max_length=MAX_LENGTH_NUMBER_PLATE,
        validators=[MinLengthValidator(MIN_LENGTH_NUMBER_PLATE)],
        unique=True
    )

    gps_device = models.OneToOneField(Device, null=True, on_delete=models.CASCADE)

    tenant = models.ForeignKey(Tenant, related_name='vehicles', on_delete=models.CASCADE)

    date_stored = models.DateTimeField(auto_now_add=True)

    is_disabled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.TOURISM
    )

    fuel = models.CharField(
        max_length=10,
        choices=Fuel.choices,
        default=Fuel.DIESEL
    )

    insurance_company = models.ForeignKey(
        InsuranceCompany,
        blank=True,
        null=True,
        default=None,
        related_name='vehicles',
        on_delete=models.SET_DEFAULT
    )

    policy_number = models.CharField(default='', blank=True, max_length=20)

    icon = models.PositiveSmallIntegerField(default=1)

    def delete(self, *args, **kwargs):
        self.gps_device.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return '{0} {1}'.format(self.brand, self.model)

    class Meta:
        db_table = 'Vehicle'
