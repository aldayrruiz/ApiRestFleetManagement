from rest_framework.routers import DefaultRouter

from allowed_vehicles.views import *

router = DefaultRouter()

router.register(r'', AllowedVehicleViewSet, basename='allowed_vehicles')

urlpatterns = router.urls
