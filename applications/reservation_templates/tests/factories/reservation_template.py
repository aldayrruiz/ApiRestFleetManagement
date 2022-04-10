from applications.reservation_templates.models import ReservationTemplate
from applications.tenants.tests.factories import TenantFactory
from shared.test.faker import CustomFactory

factory = CustomFactory().get()


class ReservationTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReservationTemplate

    title = factory.Faker('name')
    tenant = factory.SubFactory(TenantFactory)
