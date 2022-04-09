import uuid

from django.db import models

from applications.tenant.models import Tenant


class ReservationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    tenant = models.ForeignKey(Tenant, related_name='reservation_templates', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Reservation Template'

    def __str__(self):
        return self.title
