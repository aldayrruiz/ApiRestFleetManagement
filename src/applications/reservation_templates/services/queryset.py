from applications.reservation_templates.models import ReservationTemplate


def get_reservation_templates_queryset(user):
    return ReservationTemplate.objects.filter(tenant=user.tenant)
