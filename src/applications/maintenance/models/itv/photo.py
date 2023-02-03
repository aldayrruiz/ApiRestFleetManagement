import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from applications.maintenance.models.itv.itv import Itv
from applications.tenants.models import Tenant


class ItvPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='itv_photos', on_delete=models.CASCADE)
    itv = models.ForeignKey(Itv, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(default='maintenance/itv/none.png', upload_to='maintenance/itv')
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ItvPhoto'


@receiver(models.signals.post_delete, sender=ItvPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `ItvPhoto` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
