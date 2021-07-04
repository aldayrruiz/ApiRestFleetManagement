import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from applications.users.models import Role

logger = logging.getLogger(__name__)


class BaseUserService:

    def __init__(self):
        self.queryset = get_user_model().objects.all()


class UserSearcher(BaseUserService):

    def get(self, pk):
        user = get_object_or_404(self.queryset, pk=pk)
        return user


def get_admin():
    return get_user_model().objects.filter(role=Role.ADMIN).first()


def get_user_queryset(even_disabled=False):
    if even_disabled:
        return get_user_model().objects.all()
    else:
        return get_user_model().objects.filter(is_disabled=False)


def get_user_or_404(queryset, pk):
    try:
        user = queryset.get(pk=pk)
        logger.debug('User with id {} was found: {}'.format(user.id, user.fullname))
        return user
    except get_user_model().DoesNotExist:
        logger.exception('User with id {} not found.'.format(pk))
