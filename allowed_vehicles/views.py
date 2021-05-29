from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from vehicles.models import Vehicle


# FIXME: Change me for allowed vehicles.
class AllowedVehicleViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        """
        Request data: [id1, id2, ...]
        """
        # Get user
        user_queryset = get_user_model().objects.all()
        user = get_object_or_404(user_queryset, pk=pk)

        # Get new vehicles allowed to replace older ones
        vehicle_ids = self.request.data
        updated_allowed_vehicles = Vehicle.objects.filter(id__in=vehicle_ids)

        # If size of request data is not the same as vehicle types found in db return BAD REQUEST.
        if len(updated_allowed_vehicles) != len(vehicle_ids):
            return Response(status=HTTP_400_BAD_REQUEST)

        # Otherwise, replace allowed vehicle types and send OK
        user.allowed_vehicles.set(updated_allowed_vehicles)
        return Response(status=HTTP_200_OK)
