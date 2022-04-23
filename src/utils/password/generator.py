import random
import string

PASSWORD_LENGTH = 8
CODE_LENGTH = 6


def generate_password():
    password = ''.join(random.choice(string.ascii_letters) for i in range(PASSWORD_LENGTH))
    return password


def generate_recover_password_code():
    password = ''.join(random.choice(string.ascii_uppercase) for i in range(CODE_LENGTH))
    return password
