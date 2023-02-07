from applications.maintenance.models import Cleaning, Itv, Odometer, Wheels, Revision


def get_maintenance_operation_label(operation):
    if type(operation) == Cleaning:
        return 'limpieza'
    if type(operation) == Itv:
        return 'ITV'
    if type(operation) == Odometer:
        return 'cambio de kilometraje'
    if type(operation) == Revision:
        return 'revisión'
    if type(operation) == Wheels:
        return 'cambio de neumáticos'
