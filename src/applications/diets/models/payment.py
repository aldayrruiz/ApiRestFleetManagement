import uuid

from django.conf import settings
from django.db import models

from applications.diets.models import Diet
from applications.diets.models.type import PaymentType
from applications.tenants.models import Tenant

class DietPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=PaymentType.choices, default=PaymentType.Otros)
    liters = models.DecimalField(default=-1, max_digits=6, decimal_places=2, blank=True)  # Si la dieta es de tipo gasolina, se debe registrar el número de litros
    amount = models.DecimalField(default=0, max_digits=8, decimal_places=2)  # Amount: El importe de la dieta
    description = models.TextField(default='', blank=True)
    demand = models.BooleanField(default=False)
    diet = models.ForeignKey(Diet, related_name='payments', on_delete=models.CASCADE)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='payments', on_delete=models.CASCADE)

    class Meta:
        db_table = 'DietPayment'
