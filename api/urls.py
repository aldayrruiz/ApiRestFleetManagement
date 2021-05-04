from django.urls import re_path, path
from api.roles.user.views import *
from api.roles.admin.views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()

# User endpoints (mobile)
router.register(r'api/members/vehicles', VehicleViewSet, basename='vehicle')
router.register(r'api/members/vehicletypes', VehicleTypeViewSet, basename='vehicletype')
router.register(r'api/members/reservations', ReservationViewSet, basename='reservation')
router.register(r'api/members/tickets', TicketViewSet, basename='tickets')
router.register(r'api/members/incidents', IncidentViewSet, basename='incidents')

# Admin endpoints (web)
router.register(r'api/admin/vehicles', AdminVehicleViewSet, basename='adminvehicle')
router.register(r'api/admin/register', RegistrationViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^api/members/login/?$', obtain_auth_token, name='login'),
    path('api/admin/login/', AdminAuthToken.as_view())
]
