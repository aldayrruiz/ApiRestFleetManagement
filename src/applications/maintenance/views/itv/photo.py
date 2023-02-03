from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.maintenance.exceptions.operation_completed import MaintenanceOperationCompletedError
from applications.maintenance.serializers.itv.photo import CreateItvPhotoSerializer
from applications.users.models import User


class ItvPhotoViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateItvPhotoSerializer, responses={200: CreateItvPhotoSerializer()})
    def create(self, request):
        serializer = CreateItvPhotoSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester: User = self.request.user
        queryset = requester.itv_photos.all()
        photo = get_object_or_404(queryset, pk=pk)
        if photo.itv.completed:
            raise MaintenanceOperationCompletedError()
        photo.delete()
        return Response(status=HTTP_204_NO_CONTENT)