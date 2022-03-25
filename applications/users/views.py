import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from applications.users.exceptions.cannot_delete_himself import CannotDeleteHimselfError
from applications.users.exceptions.user_is_disabled import UserDisabledError
from applications.users.models import RecoverPassword, RecoverPasswordStatus
from applications.users.serializers.create import RegistrationSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.users.serializers.special import UpdateUserSerializer, SingleUserSerializer, \
    PartialUpdateUserSerializer, CreateRecoverPasswordSerializer, ConfirmRecoverPasswordSerializer, \
    RecoverPasswordSerializer
from applications.users.services.queryset import get_user_queryset
from shared.permissions import ONLY_AUTHENTICATED, ONLY_ADMIN, ALLOW_UNAUTHENTICATED
from utils.api.query import query_bool
from utils.email.users import send_create_recover_password, send_confirmed_recovered_password
from utils.password.generator import generate_password

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):
    """
    This entire endpoint class and its methods (endpoints) are only available if requester is admin.
    """

    @swagger_auto_schema(responses={200: SimpleUserSerializer(many=True)})
    def list(self, request):
        """
        List users.
        """
        requester = self.request.user
        even_disabled = query_bool(self.request, 'evenDisabled')
        logger.info(f'List users request received. [evenDisabled: {even_disabled}]')
        queryset = get_user_queryset(requester.tenant, even_disabled=even_disabled)
        serializer = SimpleUserSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SingleUserSerializer()})
    def retrieve(self, request, pk=None):
        """
        Retrieve an user.
        """
        requester = self.request.user
        logger.info('Retrieve user request received.')
        queryset = get_user_queryset(requester.tenant, even_disabled=True)
        user = get_object_or_404(queryset, pk=pk)
        serializer = SingleUserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Delete an user.
        """
        logger.info('Destroy user request received.')
        requester = self.request.user
        queryset = get_user_queryset(requester.tenant, even_disabled=True)
        user = get_object_or_404(queryset, pk=pk)
        if requester == user:
            raise CannotDeleteHimselfError()
        user.delete()
        logger.info('User was disabled.')
        return Response(status=HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=UpdateUserSerializer, responses={200: UpdateUserSerializer()})
    def update(self, request, pk=None):
        """
        Update a user.
        """
        logger.info('Update user request received.')
        requester = self.request.user
        queryset = get_user_queryset(requester.tenant, even_disabled=True)

        user = get_object_or_404(queryset, pk=pk)
        serializer = UpdateUserSerializer(user, self.request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        logger.info('User was updated')
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: PartialUpdateUserSerializer()})
    def partial_update(self, request, pk=None):
        """
        Disable and enable users.
        """
        logger.info('Partial update user request received.')
        requester = self.request.user
        queryset = get_user_queryset(requester.tenant, even_disabled=True)
        user = get_object_or_404(queryset, pk=pk)
        serializer = PartialUpdateUserSerializer(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        logger.info('User was partial updated successfully.')
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateRecoverPasswordSerializer, responses={201: RecoverPasswordSerializer()})
    @action(detail=False, methods=['post'])
    def create_recover_password(self, request):
        """
        Create a recover password instance, so user receive an email with a random code.
        """
        serializer = CreateRecoverPasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        recover_password = serializer.save()
        send_create_recover_password(recover_password.owner, recover_password.code)
        serialized = RecoverPasswordSerializer(recover_password)
        return Response(serialized.data)

    @swagger_auto_schema(request_body=ConfirmRecoverPasswordSerializer)
    @action(detail=True, methods=['put'])
    def confirm_recover_password(self, request, pk=None):
        """
        Confirm that user received the notification, sending the code received. The id param must be the id response
        from create_recover_password request.
        """
        serializer = ConfirmRecoverPasswordSerializer(data=self.request.data)
        queryset = RecoverPassword.objects.all()
        recover_password = get_object_or_404(queryset, pk=pk)
        serializer.is_valid(raise_exception=True)

        code_not_match = recover_password.code.upper() != serializer.validated_data['code'].upper()
        already_completed = recover_password.status == RecoverPasswordStatus.COMPLETED

        if code_not_match or already_completed:
            return Response(status=HTTP_400_BAD_REQUEST)

        recover_password.status = RecoverPasswordStatus.COMPLETED
        owner = recover_password.owner
        new_password = generate_password()
        owner.set_password(new_password)

        owner.save()
        recover_password.save()

        send_confirmed_recovered_password(recover_password.owner, new_password)
        return Response()

    # Create method is located in /register endpoint
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update']:
            permission_classes = ONLY_AUTHENTICATED
        elif self.action in ['create', 'destroy', 'partial_update']:
            permission_classes = ONLY_ADMIN
        else:
            permission_classes = ALLOW_UNAUTHENTICATED

        return [permission() for permission in permission_classes]


class RegistrationViewSet(viewsets.ViewSet):

    def create(self, request):
        """
        Create a user.
        """
        logger.info('Register user request received.')
        requester = self.request.user
        serializer = RegistrationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(tenant=requester.tenant)
        logger.info('User registered successfully: {}'.format(user.fullname))
        return Response(serializer.data)

    def get_permissions(self):
        permission_classes = ONLY_ADMIN
        return [permission() for permission in permission_classes]


class Login(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        logger.info('Login user request received.')
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_disabled:
            logger.info('User is disabled -> Cannot login')
            raise UserDisabledError()

        token, created = Token.objects.get_or_create(user=user)
        if created:
            logger.debug('Token was created.')
        if token.key:
            logger.info('Login was successfully.')
        else:
            logger.warning('Login of user {} failed.', user.fullname)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'fullname': user.fullname,
            'role': user.role,
            'tenant': user.tenant.id
        })
