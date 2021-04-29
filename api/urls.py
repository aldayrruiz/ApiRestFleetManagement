from django.urls import re_path
from api.roles.user.views import *
from api.roles.admin.views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
urlpatterns = router.urls

# User endpoints (mobile)
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'vehicletypes', VehicleTypeViewSet, basename='vehicletype')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'incidents', IncidentViewSet, basename='incidents')

urlpatterns += [
    re_path(r'^login/?$', obtain_auth_token, name='login')
]

# Admin endpoints (web)
router.register(r'admin/vehicles', AdminVehicleViewSet, basename='adminvehicle')
