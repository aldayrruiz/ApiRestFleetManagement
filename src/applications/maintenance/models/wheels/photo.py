import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from applications.maintenance.models.wheels.wheels import Wheels
from applications.tenants.models import Tenant


class WheelsPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wheels_photos', on_delete=models.CASCADE)
    wheels = models.ForeignKey(Wheels, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(default='maintenance/wheels/none.png', upload_to='maintenance/wheels')
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='wheels_photos', on_delete=models.CASCADE)

    class Meta:
        db_table = 'WheelsPhoto'


@receiver(models.signals.post_delete, sender=WheelsPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `WheelsPhoto` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
