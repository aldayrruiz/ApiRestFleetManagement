from django.db import models


class Device(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    imei = models.CharField(max_length=20)

    class Meta:
        db_table = 'Device'
