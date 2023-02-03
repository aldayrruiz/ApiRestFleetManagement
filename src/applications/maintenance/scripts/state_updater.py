from applications.maintenance.services.cleaning.status import CleaningStatusUpdater
from applications.maintenance.services.itv.status import ItvStatusUpdater
from applications.maintenance.services.revision.status import RevisionStatusUpdater
from applications.maintenance.services.wheels.status import WheelsStatusUpdater
from applications.tenants.models import Tenant

tenants = Tenant.objects.all()

for tenant in tenants:
    CleaningStatusUpdater(tenant).update()
    ItvStatusUpdater(tenant).update()
    RevisionStatusUpdater(tenant).update()
    WheelsStatusUpdater(tenant).update()
