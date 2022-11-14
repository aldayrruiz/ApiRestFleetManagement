import uuid

from django.db import models

from applications.tenants.models import Tenant
from applications.users.models.history_action_type import ActionType
from applications.vehicles.models import Vehicle


class VehicleRegistrationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=ActionType.choices, default=ActionType.CREATED)
    vehicle = models.ForeignKey(Vehicle, related_name='registration_history', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='vehicle_registration_history', on_delete=models.CASCADE)

    class Meta:
        db_table = 'VehicleRegistrationHistory'
        ordering = ['-date']

    def __str__(self):
        return '{} - {}'.format(self.vehicle, self.action)
