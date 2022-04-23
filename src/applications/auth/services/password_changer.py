from utils.email.users import send_created_user_email
from utils.password.generator import generate_password


class PasswordChanger:

    def __init__(self, user):
        self.user = user
        self.password = generate_password()

    def send_email(self):
        self.__change_password__()
        send_created_user_email(self.user, self.password)

    def __change_password__(self):
        self.user.set_password(self.password)
        self.user.save()
