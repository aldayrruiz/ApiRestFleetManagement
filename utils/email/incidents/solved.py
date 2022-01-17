from applications.incidents.models import IncidentType, Incident
from utils.email.shared import create_message, send_email

incident_was_solved_body = """
La incidencia que previamente reportaste ha sido solucionada.

Incidencia:
    Título: {}
    Tipo: {}    
    Fecha: {}
    Descripción: 
    {}

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


def send_incident_was_solved_email(incident: Incident):
    receiver_email = incident.owner.email
    message = get_incident_was_solved_message(receiver_email=receiver_email, incident=incident)
    send_email(receiver_email=receiver_email, message=message)


def get_incident_was_solved_message(receiver_email, incident):
    reservation = incident.reservation
    vehicle = reservation.vehicle

    incident_type = IncidentType(incident.type).label
    subject = 'Incidencia solucionada: {0} {1} - {2}'.format(vehicle.brand, vehicle.model, incident_type)
    body = incident_was_solved_body.format(
        incident.title, incident_type, incident.date_stored, incident.description,
        vehicle.brand, vehicle.model, vehicle.number_plate,
        reservation.title, reservation.start, reservation.end, reservation.description
    )

    return create_message(receiver_email=receiver_email, subject=subject, body=body)
