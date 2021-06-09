from applications.incidents.models import IncidentType
from utils.email.shared import read_config, create_message, send_email

incident_was_created_body = """
Se ha reportado una incidencia.

Incidencia:
    Título: {}
    Tipo: {}    
    Fecha: {}
    Descripción: 
    {}

Usuario:
    Username: {}
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
    email_config = read_config()

    sender_email = email_config['sender_email']
    receiver_email = admin.email

    message = get_incident_was_created_message(sender_email, receiver_email, incident)
    send_email(email_config, receiver_email, message)


def get_incident_was_created_message(sender_email, receiver_email, incident):
    owner = incident.owner
    reservation = incident.reservation
    vehicle = reservation.vehicle

    incident_type = IncidentType(incident.type).label
    subject = 'Incidencia: {0} {1} - {2}'.format(vehicle.brand, vehicle.model, incident_type)
    body = incident_was_created_body.format(
        incident.title, incident_type, incident.date_stored, incident.description,
        owner.username, owner.email,
        vehicle.brand, vehicle.model, vehicle.number_plate,
        reservation.title, reservation.start, reservation.end, reservation.description
    )

    return create_message(sender_email, receiver_email, subject, body)
