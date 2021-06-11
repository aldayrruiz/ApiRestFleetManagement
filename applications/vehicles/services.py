from applications.vehicles.models import Vehicle


class BaseVehicleService:

    def __init__(self):
        self.queryset = Vehicle.objects.all()


class VehicleSearcher(BaseVehicleService):

    def filter(self, pks):
        return self.queryset.filter(id__in=pks)

    def get(self, pk=None):
        return self.queryset.get(pk=pk)


def get_vehicle_queryset(even_disabled=False):
    if even_disabled:
        Vehicle.objects.all()
    else:
        Vehicle.objects.filter(is_disabled=False)
