import wsgi

from applications.vehicles.models import Vehicle, VehicleRegistrationHistory


vehicles = Vehicle.objects.all()
for vehicle in vehicles:
    registration = VehicleRegistrationHistory(vehicle=vehicle, tenant=vehicle.tenant)
    registration.save()
    registration.date = vehicle.date_stored
    registration.save()
