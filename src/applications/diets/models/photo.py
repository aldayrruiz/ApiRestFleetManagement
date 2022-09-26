import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from applications.diets.models.payment import DietPayment
from applications.tenants.models import Tenant


class DietPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(DietPayment, related_name='photos', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='diet_photos', on_delete=models.CASCADE)
    photo = models.ImageField(default='diet/none.png', upload_to='diets')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DietPhoto'


@receiver(models.signals.post_delete, sender=DietPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `DietPhoto` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
