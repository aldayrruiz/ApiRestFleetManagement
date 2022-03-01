from rest_framework import serializers

from utils.dates import is_after_now


def validate_reservation_dates(data):
    if not is_after_now(data['start']):
        raise serializers.ValidationError('No se puede reservar para el pasado.')

    # Check reservation's start date < end date
    if data['start'] > data['end']:
        raise serializers.ValidationError("La fecha de la comienzo debe ser anterior a la final")

    if (data['end'] - data['start']).days > 3:
        raise serializers.ValidationError('No se puede reservar por mas de 3 días.')
