from django.contrib.auth import get_user_model

from applications.tenants.models import Tenant
from applications.users.models import Role


def get_admins(tenant):
    return get_user_model().objects.filter(role=Role.ADMIN, tenant=tenant).all()


def get_supervisors(tenant: Tenant):
    supervisors = tenant.users.filter(is_supervisor=True)
    return supervisors


def get_interventors(tenant: Tenant):
    interventors = tenant.users.filter(is_interventor=True)
    return interventors
