from django.urls import re_path, path
from api.views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()

# User endpoints (mobile)
router.register(r'api/vehicles', VehicleViewSet, basename='vehicle')
router.register(r'api/users', UserViewSet, basename='user')
router.register(r'api/users/allowed-types', AllowedVehicleTypes, basename='user')
router.register(r'api/vehicle-types', VehicleTypeViewSet, basename='vehicle-type')
router.register(r'api/reservations', ReservationViewSet, basename='reservation')
router.register(r'api/tickets', TicketViewSet, basename='tickets')
router.register(r'api/incidents', IncidentViewSet, basename='incidents')

router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', obtain_auth_token, name='login'),
    path('api/admin/login/', AdminAuthToken.as_view())
]
