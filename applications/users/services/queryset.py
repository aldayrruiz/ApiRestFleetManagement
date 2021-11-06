import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def get_user_queryset(tenant, even_disabled=False):
    if not even_disabled:
        queryset = get_user_model().objects.filter(tenant=tenant, is_disabled=False)
        return queryset
    else:
        queryset = get_user_model().objects.filter(tenant=tenant)
        return queryset

