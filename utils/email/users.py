from utils.email.shared import send_email, create_message


user_created_body = """
Se te ha registrado en {}, ahora puedes hacer uso de su aplicación móvil.
Tus datos son los siguientes, recuerda que puedes cambiarlos una vez entres en la app.

Nombre Completo: {}
Email: {}
Contraseña: {}

La app puede ser encontrada en...

Play Store (teléfonos Android): https://play.google.com/store/apps/details?id=eu.bluece.fleetmanagement&gl=ES

Apple Store (teléfonos iPhone): https://apps.apple.com/es/app/bluece-fleet-management/id1590842892

"""


def send_created_user_email(user, password):
    receiver_email = user.email
    message = get_user_created_message(user=user, password=password)
    send_email(receiver_email=receiver_email, message=message)


def get_user_created_message(user, password):

    enterprise = 'Fleet Management'

    subject = 'Registro en {}'.format(enterprise)
    body = user_created_body.format(
        enterprise,
        user.fullname,
        user.email,
        password,
    )

    return create_message(receiver_email=user.email, subject=subject, body=body)

