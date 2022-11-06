import wsgi

from applications.users.models import User, UserRegistrationHistory


users = User.objects.all()
for user in users:
    registration = UserRegistrationHistory(user=user, tenant=user.tenant)
    registration.save()
    registration.date = user.date_joined
    registration.save()
