from applications.vehicles.exceptions.not_all_vehicles_were_found import NotAllVehiclesWereFoundError
from applications.vehicles.services.queryset import get_vehicles_queryset


def check_if_all_vehicles_were_found(vehicle_ids, vehicles):
    if len(vehicles) != len(vehicle_ids):
        raise NotAllVehiclesWereFoundError()


def update_allowed_vehicles(user, vehicles):
    user.allowed_vehicles.set(vehicles)


class AllowedVehiclesUpdater:
    def __init__(self, requester):
        self.requester = requester

    def update(self, user, vehicle_ids):
        vehicles = self.get_vehicles_from_ids(vehicle_ids)
        check_if_all_vehicles_were_found(vehicle_ids, vehicles)
        update_allowed_vehicles(user, vehicles)

    def get_vehicles_from_ids(self, vehicle_ids):
        queryset = get_vehicles_queryset(self.requester)
        new_vehicles = queryset.filter(id__in=vehicle_ids)
        return new_vehicles




