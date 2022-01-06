import random
import string

from applications.users.models import CODE_LENGTH
from applications.users.models import PASSWORD_LENGTH


def generate_password():
    password = ''.join(random.choice(string.ascii_letters) for i in range(PASSWORD_LENGTH))
    return password


def generate_recover_password_code():
    password = ''.join(random.choice(string.ascii_uppercase) for i in range(CODE_LENGTH))
    return password
