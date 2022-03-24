from django.urls import re_path
from rest_framework.routers import DefaultRouter

from applications.allowed_vehicles.views import AllowedVehicleViewSet
from applications.incidents.views import IncidentViewSet
from applications.insurance_companies.views import InsuranceCompanyViewSet
from applications.reservation_templates.views import ReservationTemplateViewSet
from applications.reservations.views import ReservationViewSet
from applications.tenant.views import TenantViewSet
from applications.tickets.views import TicketViewSet
from applications.traccar.views import PositionViewSet, ReservationReportViewSet
from applications.users.views import UserViewSet, Login, RegistrationViewSet
from applications.vehicles.views import VehicleViewSet

router = DefaultRouter()

router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'insurance-companies', InsuranceCompanyViewSet, basename='insurance_companies')
router.register(r'tenants', TenantViewSet, basename='tenants')
router.register(r'users', UserViewSet, basename='user')
router.register(r'users/allowed-vehicles', AllowedVehicleViewSet, basename='allowed_vehicles')
router.register(r'reservation-templates', ReservationTemplateViewSet, basename='reservation_templates')
router.register(r'incidents', IncidentViewSet, basename='incidents')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'reservations/reports', ReservationReportViewSet, basename='reports')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', Login.as_view(), name='login')
]
