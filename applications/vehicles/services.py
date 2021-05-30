from applications.vehicles.models import Vehicle


class BaseVehicleService:

    def __init__(self):
        self.queryset = Vehicle.objects.all()


class VehicleSearcher(BaseVehicleService):

    def filter(self, pks):
        return self.queryset.filter(id__in=pks)

    def get(self, pk=None):
        return self.queryset.get(pk=pk)
