from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response

from applications.maintenance.serializers.itv.photo import CreateItvPhotoSerializer
from shared.permissions import ONLY_AUTHENTICATED


class ItvPhotoViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CreateItvPhotoSerializer, responses={200: CreateItvPhotoSerializer()})
    def create(self, request):
        serializer = CreateItvPhotoSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = ONLY_AUTHENTICATED
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]
