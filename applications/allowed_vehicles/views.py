import logging

from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from applications.allowed_vehicles.services.updater import update_allowed_vehicles
from applications.users.services.queryset import get_user_queryset
from applications.vehicles.services.queryset import get_vehicles_queryset
from shared.permissions import IsAdmin

logger = logging.getLogger(__name__)


class AllowedVehicleViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        """
        Request data: [id1, id2, ...]
        """
        requester = self.request.user
        logger.info('Update user allowed vehicles request received.')
        user_queryset = get_user_queryset(requester.tenant, even_disabled=True)
        user = get_object_or_404(user_queryset, pk=pk)

        # Get new vehicles allowed to replace older ones (vehicles_queryset == vehicles in same tenant as admin)
        vehicle_ids = self.request.data
        vehicles_queryset = get_vehicles_queryset(requester)
        new_allowed_vehicles = vehicles_queryset.filter(id__in=vehicle_ids)

        # If size of request data is not the same as vehicle types found in db return BAD REQUEST.
        if len(new_allowed_vehicles) != len(vehicle_ids):
            logger.error('There are some vehicles that could not be found.')
            return Response(status=HTTP_400_BAD_REQUEST)

        # Otherwise, replace allowed vehicle types and send OK
        update_allowed_vehicles(user, new_allowed_vehicles)
        return Response(status=HTTP_200_OK)

    def get_permissions(self):
        """
        Only admin can modify vehicle privileges of users.
        """
        return [permission() for permission in [permissions.IsAuthenticated, IsAdmin]]
