import logging

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from applications.allowed_vehicles.services import AllowedVehicleUpdater
from applications.users.services import UserSearcher
from applications.vehicles.services import VehicleSearcher
from shared.permissions import IsAdmin

logger = logging.getLogger(__name__)


class AllowedVehicleViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        """
        Request data: [id1, id2, ...]
        """
        logger.info('Update user allowed vehicles request received.')
        user_searcher = UserSearcher()
        user = user_searcher.get(pk=pk)

        # Get new vehicles allowed to replace older ones
        vehicle_ids = self.request.data
        vehicle_searcher = VehicleSearcher()
        new_allowed_vehicles = vehicle_searcher.filter(pks=vehicle_ids)

        # If size of request data is not the same as vehicle types found in db return BAD REQUEST.
        if len(new_allowed_vehicles) != len(vehicle_ids):
            logger.error('')
            return Response(status=HTTP_400_BAD_REQUEST)

        # Otherwise, replace allowed vehicle types and send OK
        updater = AllowedVehicleUpdater(user)
        updater.update_allowed_vehicles(new_allowed_vehicles)
        return Response(status=HTTP_200_OK)

    def get_permissions(self):
        """
        Only admin can modify vehicle privileges of users.
        """
        return [permission() for permission in [permissions.IsAuthenticated, IsAdmin]]
