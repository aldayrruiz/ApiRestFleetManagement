import logging

from django.contrib.auth import get_user_model

from applications.users.models import User
from applications.users.services.roler import Roler

logger = logging.getLogger(__name__)


def get_user_queryset(requester: User, even_disabled=False):
    tenant = requester.tenant
    if even_disabled and Roler.is_admin(requester):
        # Return all users only if requester is admin
        queryset = get_user_model().objects.filter(tenant=tenant)
        return queryset
    else:
        # Return only user that are not disabled
        queryset = get_user_model().objects.filter(tenant=tenant, is_disabled=False)
        return queryset
