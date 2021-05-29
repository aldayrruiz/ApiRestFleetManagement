from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class BaseUserService:

    def __init__(self):
        self.queryset = get_user_model().objects.all()


class UserSearcher(BaseUserService):

    def get(self, pk):
        user = get_object_or_404(self.queryset, pk=pk)
        return user
