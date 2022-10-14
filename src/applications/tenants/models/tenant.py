import uuid

from django.db import models


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    short_name = models.CharField(default='', null=True, blank=True, max_length=50)
    name = models.CharField(max_length=50, unique=True)
    diet = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='tenants/logos', blank=True, null=True)
    date_stored = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Tenant'

    def __str__(self):
        return self.name
