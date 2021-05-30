from django.urls import re_path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from applications.allowed_vehicles.views import AllowedVehicleViewSet
from applications.incidents.views import IncidentViewSet
from applications.reservations.views import ReservationViewSet
from applications.tickets.views import TicketViewSet
from applications.users.views import UserViewSet, AdminAuthToken, RegistrationViewSet
from applications.vehicles.views import VehicleViewSet

router = DefaultRouter()

router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'users', UserViewSet, basename='user')
router.register(r'users/allowed-vehicles', AllowedVehicleViewSet, basename='allowed_vehicles')
router.register(r'incidents', IncidentViewSet, basename='incidents')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^user/login/?$', obtain_auth_token, name='user_login'),
    re_path(r'^admin/login/?$', AdminAuthToken.as_view(), name='admin_login')
]
