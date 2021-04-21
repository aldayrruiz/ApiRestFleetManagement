from django.urls import path, re_path
from api.views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'vehicletypes', VehicleTypeViewSet, basename='vehicletype')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'incidents', IncidentViewSet, basename='incidents')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', obtain_auth_token, name='login')
]
