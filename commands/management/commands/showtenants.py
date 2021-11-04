from django.core.management.base import BaseCommand, CommandError

from applications.tenant.models import Tenant


class Command(BaseCommand):
    help = 'Create a tenant'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if len(tenants):
            self.stdout.write(self.style.SUCCESS('Tenant name: Tenant id'))
            for tenant in tenants:
                self.stdout.write(self.style.SUCCESS('{}: {}'.format(tenant.name, tenant.id)))
        else:
            raise CommandError('There are not tenants. Use python manage.py createtenant <Tenant name>')
