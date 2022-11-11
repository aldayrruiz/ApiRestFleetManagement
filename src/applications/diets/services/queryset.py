from applications.diets.models import Diet, DietPayment, DietMonthlyPdfReport
from applications.users.models import User, Role


def get_diet_queryset(requester: User, take_all=False):
    tenant = requester.tenant
    if requester.role in [Role.ADMIN, Role.SUPER_ADMIN] and take_all:
        # Return all diets only if requester is admin
        queryset = Diet.objects.filter(tenant=tenant)
    else:
        # Otherwise return only diets that belong to requester
        queryset = Diet.objects.filter(tenant=tenant, owner=requester)
    return queryset


def get_diet_payment_queryset(requester: User, take_all=False):
    tenant = requester.tenant
    if requester.role in [Role.ADMIN, Role.SUPER_ADMIN] and take_all:
        # Return all diets only if requester is admin
        queryset = DietPayment.objects.filter(tenant=tenant)
    else:
        # Otherwise return only diets that belong to requester
        queryset = DietPayment.objects.filter(tenant=tenant, owner=requester)
    return queryset


def get_diet_reports_queryset(user):
    return DietMonthlyPdfReport.objects.filter(tenant=user.tenant)
