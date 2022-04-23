from django.core.management.base import CommandError, BaseCommand

from applications.tenants.models import Tenant
from applications.users.models import User


class Command(BaseCommand):
    help = 'Create a superuser, and allow password to be provided'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            dest='email',
            default=None,
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--fullname',
            dest='fullname',
            default=None,
            help='Specifies the fullname for the superuser.',
        )
        parser.add_argument(
            '--password',
            dest='password',
            default=None,
            help='Specifies the password for the superuser.',
        )
        parser.add_argument(
            '--tenant-name',
            dest='tenant-name',
            default=None,
            help='Specifies the tenant name for the superuser.',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        fullname = options.get('fullname')
        password = options.get('password')
        tenant = options.get('tenant-name')

        # Validate user does not exists
        users_exists = User.objects.filter(email=email).exists()
        if users_exists:
            raise CommandError('User already exists')

        # Create tenant
        tenant, created = Tenant.objects.get_or_create(name=tenant)
        if not created:
            self.stdout.write(self.style.SUCCESS('Tenant already exists, I am using that'))

        # Create admin
        user = User.objects.create_superuser(email=email, fullname=fullname, tenant=tenant.id, password=password)
        user.set_password(password)
        user.save()

