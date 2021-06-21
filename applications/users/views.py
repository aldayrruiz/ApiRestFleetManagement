import logging

from rest_framework import viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from applications.users.serializers.create import RegistrationSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.users.serializers.special import UpdateUserSerializer, SingleUserSerializer
from applications.users.services import get_user_queryset, get_user_or_404
from shared.permissions import IsAdmin

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):
    """
    This entire endpoint class and its methods (endpoints) are only available if requester is admin.
    """

    def list(self, request):
        """
        It returns all users.
        :param request:
        :return: users
        """
        logger.info('List users request received.')
        queryset = get_user_queryset()
        serializer = SimpleUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        It returns the user given an id.
        :param request:
        :param pk: user id
        :return:
        """
        logger.info('Retrieve user request received.')
        queryset = get_user_queryset()
        user = get_user_or_404(queryset, pk=pk)
        serializer = SingleUserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        It disables an user.
        If requester tries to delete himself, server respond with 403 ERROR.
        :param request:
        :param pk: user id
        :return:
        """
        logger.info('Destroy user request received.')
        requester = self.request.user
        queryset = get_user_queryset()
        user = get_user_or_404(queryset, pk=pk)
        if requester == user:
            logger.warning("User couldn't delete himself.")
            return Response(status=HTTP_403_FORBIDDEN)
        user.is_disabled = True
        logger.info('User was disabled.')
        return Response(status=HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        """
        It update the data of a user.
        """
        logger.info('Update user request received.')
        requester = self.request.user
        queryset = get_user_queryset()
        user = get_user_or_404(queryset, pk=pk)
        serializer = UpdateUserSerializer(user, self.request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info('User was updated successfully.')
            return Response(serializer.data)
        log_serializer_not_valid(serializer)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    # Create method is located in /register endpoint
    def get_permissions(self):
        return [permission() for permission in [permissions.IsAuthenticated, IsAdmin]]


class RegistrationViewSet(viewsets.ViewSet):

    def create(self, request):
        logger.info('Register user request received.')
        serializer = RegistrationSerializer(data=self.request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info('User register successfully: {}'.format(user.fullname))
            return Response(serializer.data)
        log_serializer_not_valid(serializer)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        # Only admin can register users.
        return [permission() for permission in [permissions.IsAuthenticated, IsAdmin]]


class Login(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        logger.info('Login user request received.')
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if created:
            logger.debug('Token was created because.')
        if token.key:
            logger.info('Login was successfully.')
        else:
            logger.warning('Login of user {} failed.', user.fullname)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'role': user.role
        })


def log_serializer_not_valid(serializer):
    logger.error("User couldn't be serialized with {} because of {}."
                 .format(serializer.__class__.__name__, serializer.errors))
