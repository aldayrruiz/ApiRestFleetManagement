from applications.maintenance.services.cleaning.status import CleaningStatusUpdater
from applications.maintenance.services.emails.pending import MaintenanceOperationPendingEmail
from applications.maintenance.services.itv.status import ItvStatusUpdater
from applications.maintenance.services.revision.status import RevisionStatusUpdater
from applications.maintenance.services.wheels.status import WheelsStatusUpdater
from applications.tenants.models import Tenant

tenants = Tenant.objects.all()

for tenant in tenants:
    cleaning_updater = CleaningStatusUpdater(tenant)
    cleaning_updater.update()
    itv_updater = ItvStatusUpdater(tenant)
    itv_updater.update()
    revision_updater = RevisionStatusUpdater(tenant)
    revision_updater.update()
    wheels_updater = WheelsStatusUpdater(tenant)
    wheels_updater.update()

    for cleaning in cleaning_updater.updates_to_pending:
        MaintenanceOperationPendingEmail(tenant, cleaning, 'limpieza').send()

    for cleaning in cleaning_updater.updates_to_expired:
        MaintenanceOperationPendingEmail(tenant, cleaning, 'limpieza').send()

    for itv in itv_updater.updates_to_pending:
        MaintenanceOperationPendingEmail(tenant, itv, 'ITV').send()

    for itv in itv_updater.updates_to_expired:
        MaintenanceOperationPendingEmail(tenant, itv, 'ITV').send()

    for revision in revision_updater.updates_to_pending:
        MaintenanceOperationPendingEmail(tenant, revision, 'revisión').send()

    for revision in revision_updater.updates_to_expired:
        MaintenanceOperationPendingEmail(tenant, revision, 'revisión').send()

    for wheels in wheels_updater.updates_to_pending:
        MaintenanceOperationPendingEmail(tenant, wheels, 'cambio de neumáticos').send()

    for wheels in wheels_updater.updates_to_expired:
        MaintenanceOperationPendingEmail(tenant, wheels, 'cambio de neumáticos').send()
