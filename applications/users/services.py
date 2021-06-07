from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from applications.users.models import Role


class BaseUserService:

    def __init__(self):
        self.queryset = get_user_model().objects.all()


class UserSearcher(BaseUserService):

    def get(self, pk):
        user = get_object_or_404(self.queryset, pk=pk)
        return user


def get_admin():
    return get_user_model().objects.filter(role=Role.ADMIN).first()
