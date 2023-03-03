from django.urls import re_path
from rest_framework.routers import DefaultRouter

from applications.allowed_vehicles.views import AllowedVehicleViewSet
from applications.auth.views import AuthViewSet
from applications.diets.views import DietPaymentViewSet, DietViewSet, DietPhotoViewSet, DietMonthlyPdfReportViewSet
from applications.incidents.views import IncidentViewSet
from applications.insurance_companies.views import InsuranceCompanyViewSet
from applications.maintenance.views.cleaning import CleaningViewSet, CleaningPhotoViewSet, CleaningCardViewSet
from applications.maintenance.views.itv import ItvViewSet, ItvPhotoViewSet
from applications.maintenance.views.odometer import OdometerViewSet, OdometerPhotoViewSet
from applications.maintenance.views.odometer.card import OdometerCardViewSet
from applications.maintenance.views.repairment.photo import RepairmentPhotoViewSet
from applications.maintenance.views.repairment.repairment import RepairmentViewSet
from applications.maintenance.views.revision import RevisionViewSet, RevisionPhotoViewSet
from applications.maintenance.views.wheels import WheelsViewSet, WheelsPhotoViewSet
from applications.reports.views import ReportViewSet
from applications.reservation_templates.views import ReservationTemplateViewSet
from applications.reservations.views import ReservationViewSet, PaginatedReservationViewSet
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
router.register(r'paginated-reservations', PaginatedReservationViewSet, basename='paginated_reservations')

router.register(r'reservations/reports', ReservationReportViewSet, basename='reports')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'register', RegistrationViewSet, basename='register')

# Diets
router.register(r'diets', DietViewSet, basename='diets')
router.register(r'diet-payments', DietPaymentViewSet, basename='diet_payments')
router.register(r'diet-photos', DietPhotoViewSet, basename='diet_photos')

# Maintenance
router.register(r'maintenance/cleanings', CleaningViewSet, basename='cleanings')
router.register(r'maintenance/cleaning-photos', CleaningPhotoViewSet, basename='cleaning_photos')
router.register(r'maintenance/cleaning-cards', CleaningCardViewSet, basename='cleaning_cards')
router.register(r'maintenance/itvs', ItvViewSet, basename='itvs')
router.register(r'maintenance/itv-photos', ItvPhotoViewSet, basename='itv_photos')
router.register(r'maintenance/odometers', OdometerViewSet, basename='odometers')
router.register(r'maintenance/odometer-photos', OdometerPhotoViewSet, basename='odometers_photos')
router.register(r'maintenance/odometer-cards', OdometerCardViewSet, basename='odometers_cards')
router.register(r'maintenance/revisions', RevisionViewSet, basename='revisions')
router.register(r'maintenance/revision-photos', RevisionPhotoViewSet, basename='revision_photos')
router.register(r'maintenance/wheels', WheelsViewSet, basename='wheels')
router.register(r'maintenance/wheels-photos', WheelsPhotoViewSet, basename='wheels_photos')
router.register(r'maintenance/repairments', RepairmentViewSet, basename='repairments')
router.register(r'maintenance/repairment-photos', RepairmentPhotoViewSet, basename='repairment_photos')

# Informes
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'diet-reports', DietMonthlyPdfReportViewSet, basename='diet_reports')
router.register(r'billing-reports', TenantBillingMonthlyPdfReportViewSet, basename='billing_reports')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', Login.as_view(), name='login'),
]
