import uuid

from django.conf import settings
from django.db import models
from applications.reservations.models import Reservation
from applications.tenants.models import Tenant


class Diet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(Reservation, related_name='diet', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='diets', on_delete=models.CASCADE)
    # Start & end are fields completed by the user. They are used to know if entire day or half day diet is needed.
    start = models.DateTimeField()
    end = models.DateTimeField()
    number_of_diets = models.DecimalField(default=0, max_digits=3, decimal_places=1)
    completed = models.BooleanField(default=False)
    modified = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='diets', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Diet'
