from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from applications.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Create a tenant'

    def add_arguments(self, parser):
        parser.add_argument('names', nargs='+', type=str)

    def handle(self, *args, **options):
        arr = options['names']
        tenant_name = ' '.join(arr)
        try:
            tenant = Tenant.objects.create(name=tenant_name)
        except IntegrityError:
            raise CommandError('Tenant with that name already exists.')

        self.stdout.write(self.style.SUCCESS('Tenant {} with id {} created'.format(tenant.name, tenant.id)))
