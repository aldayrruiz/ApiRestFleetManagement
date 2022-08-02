import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.auth.services.password_changer import PasswordChanger
from applications.users.services.queryset import get_user_queryset
from shared.permissions import ONLY_ADMIN_OR_SUPER_ADMIN

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    @swagger_auto_schema()
    @action(detail=True, methods=['post'])
    def resend_registration_email(self, request, pk=None):
        logger.info('Retrieve user request received.')
        requester = self.request.user
        queryset = get_user_queryset(requester, even_disabled=True)
        user = get_object_or_404(queryset, pk=pk)
        password_changer = PasswordChanger(user)
        password_changer.send_email()
        return Response()

    def get_permissions(self):
        permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]
