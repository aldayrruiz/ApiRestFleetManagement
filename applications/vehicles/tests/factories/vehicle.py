from faker.factory import Factory

from applications.insurance_companies.tests.factories import InsuranceCompanyFactory
from applications.traccar.tests.factories import DeviceFactory
from applications.vehicles.models import Vehicle
from applications.tenants.tests.factories import TenantFactory
from shared.test.faker import CustomFactory


Faker = Factory.create
fake = Faker()
fake.seed(0)


factory = CustomFactory().get()


def number_plate_generator():
    return fake.hexify(text='^'*7, upper=True)


def policy_number_generator():
    return fake.hexify(text='^'*20)


class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle

    brand = factory.Faker('vehicle_make')
    model = factory.Faker('vehicle_model')
    number_plate = factory.LazyFunction(number_plate_generator)
    gps_device = factory.SubFactory(DeviceFactory)
    tenant = factory.SubFactory(TenantFactory)
    insurance_company = factory.SubFactory(InsuranceCompanyFactory)
    policy_number = factory.LazyFunction(policy_number_generator)
