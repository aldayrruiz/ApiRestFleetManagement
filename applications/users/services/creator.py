from decouple import config
from django.contrib.auth import get_user_model


def create_admin(email, fullname, tenant, password):
    return get_user_model().objects.create_superuser(email, fullname, tenant, password)


def create_fake_admin(fake_tenant):
    fullname = config('FAKE_ADMIN_FULLNAME')
    email = config('FAKE_ADMIN_EMAIL')
    password = config('FAKE_ADMIN_PASSWORD')
    return create_admin(email, fullname, fake_tenant, password)
