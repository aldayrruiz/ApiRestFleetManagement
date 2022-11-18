from django.urls import re_path, path
from rest_framework.routers import DefaultRouter

from applications.allowed_vehicles.views import AllowedVehicleViewSet
from applications.auth.views import AuthViewSet
from applications.diets.views import DietPaymentViewSet, DietViewSet, DietPhotoViewSet, DietMonthlyPdfReportViewSet
from applications.incidents.views import IncidentViewSet
from applications.insurance_companies.views import InsuranceCompanyViewSet
from applications.reports.views import ReportViewSet
from applications.reservation_templates.views import ReservationTemplateViewSet
from applications.reservations.views import ReservationViewSet, NewReservationViewSet
from applications.tenants.views import TenantViewSet, TenantBillingMonthlyPdfReportViewSet
from applications.tickets.views import TicketViewSet
from applications.traccar.views import PositionViewSet, ReservationReportViewSet
from applications.users.views import UserViewSet, Login, RegistrationViewSet
from applications.vehicles.views import VehicleViewSet

router = DefaultRouter()

router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'insurance-companies', InsuranceCompanyViewSet, basename='insurance_companies')
router.register(r'tenants', TenantViewSet, basename='tenants')
router.register(r'users', UserViewSet, basename='users')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users/allowed-vehicles', AllowedVehicleViewSet, basename='allowed_vehicles')
router.register(r'reservation-templates', ReservationTemplateViewSet, basename='reservation_templates')
router.register(r'incidents', IncidentViewSet, basename='incidents')
router.register(r'reservations', ReservationViewSet, basename='reservations')
router.register(r'new_reservations', NewReservationViewSet, basename='new_reservations')

router.register(r'reservations/reports', ReservationReportViewSet, basename='reports')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'register', RegistrationViewSet, basename='register')

# Diets
router.register(r'diets', DietViewSet, basename='diets')
router.register(r'diet-payments', DietPaymentViewSet, basename='diet_payments')
router.register(r'diet-photos', DietPhotoViewSet, basename='diet_photos')

# Informes
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'diet-reports', DietMonthlyPdfReportViewSet, basename='diet_reports')
router.register(r'billing-reports', TenantBillingMonthlyPdfReportViewSet, basename='billing_reports')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', Login.as_view(), name='login'),
]
