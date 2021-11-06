from django.contrib.auth import get_user_model

from applications.users.models import Role


def get_admin(tenant):
    return get_user_model().objects.filter(role=Role.ADMIN, tenant=tenant).first()
