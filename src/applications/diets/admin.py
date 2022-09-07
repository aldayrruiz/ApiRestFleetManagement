from django.contrib import admin

from applications.diets.models.diet import Diet, DietPhoto, DietCollection

admin.site.register(Diet)
admin.site.register(DietPhoto)
admin.site.register(DietCollection)
