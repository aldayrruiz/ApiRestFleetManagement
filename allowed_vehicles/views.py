from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from allowed_vehicles.services import AllowedVehicleUpdater
from users.services import UserSearcher
from vehicles.services import VehicleSearcher


class AllowedVehicleViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        """
        Request data: [id1, id2, ...]
        """
        user_searcher = UserSearcher()
        user = user_searcher.get(pk=pk)

        # Get new vehicles allowed to replace older ones
        vehicle_ids = self.request.data
        vehicle_searcher = VehicleSearcher()
        new_allowed_vehicles = vehicle_searcher.filter(pks=vehicle_ids)

        # If size of request data is not the same as vehicle types found in db return BAD REQUEST.
        if len(new_allowed_vehicles) != len(vehicle_ids):
            return Response(status=HTTP_400_BAD_REQUEST)

        # Otherwise, replace allowed vehicle types and send OK
        updater = AllowedVehicleUpdater(user)
        updater.update_allowed_vehicles(new_allowed_vehicles)
        return Response(status=HTTP_200_OK)
