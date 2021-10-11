import logging

from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404

from applications.users.models import Role

logger = logging.getLogger(__name__)


class BaseUserService:

    def __init__(self):
        self.queryset = get_user_model().objects.filter(is_fake=False)


class UserSearcher(BaseUserService):

    def get(self, pk):
        user = get_object_or_404(self.queryset, pk=pk)
        return user


def get_admin():
    return get_user_model().objects.filter(role=Role.ADMIN).first()


def get_user_queryset(even_disabled=False, even_fakes=False):
    if not even_disabled and not even_fakes:
        queryset = get_user_model().objects.filter(is_disabled=False, is_fake=False)
        return queryset
    if even_disabled and not even_fakes:
        queryset = get_user_model().objects.filter(is_fake=False)
        return queryset
    elif not even_disabled and even_fakes:
        queryset = get_user_model().objects.filter(is_disabled=False)
        return queryset
    else:
        queryset = get_user_model().objects.all()
        return queryset


def get_user_or_404(queryset, pk):
    try:
        user = queryset.get(pk=pk)
        logger.debug('User with id {} was found: {}'.format(user.id, user.fullname))
        return user
    except get_user_model().DoesNotExist:
        logger.exception('User with id {} not found.'.format(pk))


def delete_if_fake_user_already_exists(serializer):
    user_with_same_email_and_fake = __get_user_with_same_email_and_fake__(serializer)
    if user_with_same_email_and_fake:
        user_with_same_email_and_fake.delete()


def __get_user_with_same_email_and_fake__(serializer):
    email = serializer.initial_data['email']
    return get_user_model().objects.filter(email=email, is_fake=True).first()
