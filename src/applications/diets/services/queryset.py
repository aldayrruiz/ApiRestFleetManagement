from applications.diets.models.diet import DietCollection, Diet
from applications.users.models import User, Role


def get_diet_collection_queryset(requester: User, take_all=False):
    tenant = requester.tenant
    if requester.role in [Role.ADMIN, Role.SUPER_ADMIN] and take_all:
        # Return all diets only if requester is admin
        queryset = DietCollection.objects.filter(tenant=tenant)
    else:
        # Otherwise return only diets that belong to requester
        queryset = DietCollection.objects.filter(tenant=tenant, owner=requester)
    return queryset


def get_diet_queryset(requester: User, take_all=False):
    tenant = requester.tenant
    if requester.role in [Role.ADMIN, Role.SUPER_ADMIN] and take_all:
        # Return all diets only if requester is admin
        queryset = Diet.objects.filter(tenant=tenant)
    else:
        # Otherwise return only diets that belong to requester
        queryset = Diet.objects.filter(tenant=tenant, owner=requester)
    return queryset
