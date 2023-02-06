from decouple import config

from applications.vehicles.models import Vehicle


class MaintenanceOperationEmailSender:
    @staticmethod
    def get_maintenance_url():
        base_url = config('SERVER_URL')
        return f'{base_url}/admin/maintenance/table'

    @staticmethod
    def get_vehicle_label(vehicle: Vehicle):
        return f'{vehicle.brand} {vehicle.model} - {vehicle.number_plate}'

    @staticmethod
    def get_operation_label(operation):
        return f'{operation.operation_label}'
