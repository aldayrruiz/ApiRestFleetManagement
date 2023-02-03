import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from applications.diets.models.payment import DietPayment
from applications.maintenance.models.revision.revision import Revision
from applications.tenants.models import Tenant


class RevisionPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='revision_photos', on_delete=models.CASCADE)
    revision = models.ForeignKey(Revision, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(default='maintenance/revision/none.png', upload_to='maintenance/revision')
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='revision_photos', on_delete=models.CASCADE)

    class Meta:
        db_table = 'RevisionPhoto'


@receiver(models.signals.post_delete, sender=RevisionPhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `RevisionPhoto` object is deleted.
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)
