from applications.tenants.models import Tenant


def get_tenants_queryset():
    return Tenant.objects.all()
