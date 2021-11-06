from rest_framework.exceptions import PermissionDenied


def check_if_not_mine(requester, obj):
    if requester is obj.owner:
        raise PermissionDenied('No puedes crear un ticket de tu propia reserva')


def check_if_not_admin_reservation(request, obj):
    # TODO: Check if reservation is not by an admin, because normal user cannot create a ticket of a
    #       reservation from an admin.
    raise Exception('Unsupported check: check_if_not_admin_reservation.')
