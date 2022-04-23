from faker.factory import Factory
from applications.tenants.tests.factories import TenantFactory
from applications.traccar.models import Device
from shared.test.faker import CustomFactory


Faker = Factory.create
fake = Faker()
fake.seed(0)


factory = CustomFactory().get()


def imei_generator():
    return fake.hexify(text='^^^^^^^^^^^^^^^')


class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device

    name = factory.Faker('vehicle_make')
    imei = factory.LazyFunction(imei_generator)
    tenant = factory.SubFactory(TenantFactory)
