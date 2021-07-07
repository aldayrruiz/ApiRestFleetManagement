from django.urls import re_path
from rest_framework.routers import DefaultRouter

from applications.allowed_vehicles.views import AllowedVehicleViewSet
from applications.incidents.views import IncidentViewSet
from applications.reservations.views import ReservationViewSet
from applications.tickets.views import TicketViewSet
from applications.traccar.views import PositionViewSet, ReportsRouteViewSet
from applications.users.views import UserViewSet, Login, RegistrationViewSet
from applications.vehicles.views import VehicleViewSet

router = DefaultRouter()

router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'users', UserViewSet, basename='user')
router.register(r'users/allowed-vehicles', AllowedVehicleViewSet, basename='allowed_vehicles')
router.register(r'incidents', IncidentViewSet, basename='incidents')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'register', RegistrationViewSet, basename='register')
router.register(r'route', ReportsRouteViewSet, basename='reports_reservation')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', Login.as_view(), name='login')
]
