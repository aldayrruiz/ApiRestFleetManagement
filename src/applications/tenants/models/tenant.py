import uuid

from django.db import models


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='tenants/logos', blank=True, null=True)
    date_stored = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Tenant'

    def __str__(self):
        return self.name
