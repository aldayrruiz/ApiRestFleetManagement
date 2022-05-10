from utils.email.shared import send_email, create_message, EmailSender

user_created_body = """
Se te ha registrado en {}, ahora puedes hacer uso de su aplicación móvil.
Tus datos son los siguientes, recuerda que puedes cambiarlos una vez entres en la app.

Nombre Completo: {}
Email: {}
Contraseña: {}

La app puede ser encontrada en...

Play Store (teléfonos Android): https://play.google.com/store/apps/details?id=eu.bluece.drivers

Apple Store (teléfonos iPhone): https://apps.apple.com/app/blue-drivers/id1621125347

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


create_recover_password_body = """\
Hola {}:
Has solicitado recuperar la contraseña de tu cuenta.

Si no has realizado esta solicitud puedes ignorar este mensaje y tu contraseña seguirá siendo la misma.

Si has realizado esta solicitud de recuperación de contraseña, introduce el siguiente código en la app.

{}
"""


def send_create_recover_password(user, code):
    subject = 'Fleet Management - Recuperar contraseña'
    email_sender = EmailSender(user.email, subject)
    body = create_recover_password_body.format(user.fullname, code)
    email_sender.attach_plain(body)
    email_sender.send()


confirmed_recovered_password_body = """\
Hola {}:
Se ha confirmado correctamente la recuperación de su contraseña.
Su contraseña nueva es: {}

Recuerde que puede cambiar su contraseña una vez dentro de la app.
"""


def send_confirmed_recovered_password(user, new_password):
    subject = 'Fleet Management - Recuperar contraseña'
    email_sender = EmailSender(user.email, subject)
    body = confirmed_recovered_password_body.format(user.fullname, new_password)
    email_sender.attach_plain(body)
    email_sender.send()
