from django.urls import path, re_path
from api.views import VehicleViewSet, VehicleTypeViewSet, ReservationViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'vehicletypes', VehicleTypeViewSet, basename='vehicletype')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', obtain_auth_token, name='login')
]
