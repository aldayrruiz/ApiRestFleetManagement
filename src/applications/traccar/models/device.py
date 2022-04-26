from django.db import models

from applications.tenants.models.tenant import Tenant


class Device(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    imei = models.CharField(max_length=20)
    tenant = models.ForeignKey(Tenant, related_name='devices', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Device'
