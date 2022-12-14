import logging

from django.contrib.auth import get_user_model

from applications.users.models import User, Role

logger = logging.getLogger(__name__)


def get_user_queryset(requester: User, even_disabled=False, even_deleted=False):
    tenant = requester.tenant

    # If requester is USER, return all users except disabled and deleted
    if requester.role == Role.USER:
        queryset = get_user_model().objects.filter(tenant=tenant, is_disabled=False, is_deleted=False)
        return queryset

    # If requester is ADMIN
    if even_disabled and even_deleted:
        # Admins can see all users (even disabled and deleted)
        queryset = get_user_model().objects.filter(tenant=tenant)
        return queryset
    elif even_disabled:
        # Return all users only if requester is admin
        queryset = get_user_model().objects.filter(tenant=tenant, is_deleted=False)
        return queryset
    else:
        # Return all users only if requester is admin
        queryset = get_user_model().objects.filter(tenant=tenant, is_disabled=False, is_deleted=False)
        return queryset
