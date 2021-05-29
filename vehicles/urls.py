from rest_framework.routers import DefaultRouter

from vehicles.views import *

router = DefaultRouter()

router.register(r'', VehicleViewSet, basename='vehicle')

urlpatterns = router.urls
