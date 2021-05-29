import uuid

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from vehicles.models import Vehicle


class AllowedVehicles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        db_table = 'AllowedVehicles'
        constraints = [
            UniqueConstraint(fields=['user', 'vehicle'], name='constraint_user_vehicle')
        ]

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.vehicle)
