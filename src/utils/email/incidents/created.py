from applications.incidents.models import IncidentType
from utils.email.shared import create_message, send_email

incident_was_created_body = """
Se ha reportado una incidencia.

Incidencia:
    Tipo: {}    
    Fecha: {}
    Descripción: 
    {}

Usuario:
    Fullname: {}
    Email: {}

Vehículo:
    Marca: {}
    Modelo: {}
    Matricula: {}

Reserva:
    Título: {}
    Fecha de recogida: {} 
    Fecha de entrega: {}
    Descripción: 
    {}
"""


def send_created_incident_email(admin, incident):
    receiver_email = admin.email
    message = get_incident_was_created_message(receiver_email=receiver_email, incident=incident)
    send_email(receiver_email=receiver_email, message=message)


def get_incident_was_created_message(receiver_email, incident):
    owner = incident.owner
    reservation = incident.reservation
    vehicle = reservation.vehicle

    incident_type = IncidentType(incident.type).label
    subject = 'Incidencia: {0} {1} - {2}'.format(vehicle.brand, vehicle.model, incident_type)
    body = incident_was_created_body.format(
        incident_type, incident.date_stored, incident.description,
        owner.fullname, owner.email,
        vehicle.brand, vehicle.model, vehicle.number_plate,
        reservation.title, reservation.start, reservation.end, reservation.description
    )

    return create_message(receiver_email=receiver_email, subject=subject, body=body)
