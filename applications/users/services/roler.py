from applications.users.models import Role


class Roler:
    @staticmethod
    def is_admin(user):
        return user.role in [Role.ADMIN, Role.SUPER_ADMIN]
