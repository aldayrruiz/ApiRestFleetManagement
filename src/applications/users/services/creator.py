from django.contrib.auth import get_user_model


def create_admin(email, fullname, tenant, password):
    return get_user_model().objects.create_superuser(email, fullname, tenant, password)

