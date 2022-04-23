from applications.vehicles.models import Vehicle


def get_vehicles_queryset(user):
    """
    Return the queryset of vehicles given user (tenant)
    """
    return Vehicle.objects.filter(tenant=user.tenant)
