from applications.users.models import Role
from applications.vehicles.models import Vehicle


class AllowedVehicleUpdater:

    def __init__(self, user):
        self.user = user

    def update_allowed_vehicles(self, vehicles):
        self.user.allowed_vehicles.set(vehicles)


def get_allowed_vehicles_queryset(user, even_disabled=False):
    if even_disabled:
        if user.role == Role.ADMIN:
            return Vehicle.objects.all()
        else:
            return user.allowed_vehicles.all()
    else:
        if user.role == Role.ADMIN:
            return Vehicle.objects.filter(is_disabled=False)
        else:
            return user.allowed_vehicles.all()
