import logging

from decouple import config
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


def get_user_queryset(tenant, even_disabled=False):
    if not even_disabled:
        queryset = get_user_model().objects.filter(tenant=tenant, is_disabled=False)
        return queryset
    else:
        queryset = get_user_model().objects.filter(tenant=tenant)
        return queryset


def delete_if_fake_user_already_exists(serializer):
    user_with_same_email_and_fake = __get_user_with_same_email_and_fake__(serializer)
    if user_with_same_email_and_fake:
        user_with_same_email_and_fake.delete()


def __get_user_with_same_email_and_fake__(serializer):
    email = serializer.initial_data['email']
    return get_user_model().objects.filter(email=email, is_fake=True).first()


def create_admin(email, fullname, tenant, password):
    return get_user_model().objects.create_superuser(email, fullname, tenant, password)


def create_fake_admin(fake_tenant):
    fullname = config('FAKE_ADMIN_FULLNAME')
    email = config('FAKE_ADMIN_EMAIL')
    password = config('FAKE_ADMIN_PASSWORD')
    return create_admin(email, fullname, fake_tenant, password)
