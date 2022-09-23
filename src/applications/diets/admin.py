from django.contrib import admin

from applications.diets.models import DietPayment, Diet, DietPhoto

admin.site.register(DietPayment)
admin.site.register(DietPhoto)
admin.site.register(Diet)
