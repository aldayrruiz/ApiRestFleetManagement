import requests
from decouple import config

from applications.vehicles.models import Vehicle

TRUPHONE_API_URL = config('TRUPHONE_API_URL')
TRUPHONE_API_TOKEN = config('TRUPHONE_API_TOKEN')
TELTONIKA_SMS_LOGIN = config('TELTONIKA_SMS_LOGIN')
TELTONIKA_SMS_PASSWORD = config('TELTONIKA_SMS_PASSWORD')

HEADERS = {
    'Authorization': f'Token {TRUPHONE_API_TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

SMS_SEND_COMMANDS_API_URL = f'{TRUPHONE_API_URL}/sims/send_sms'


class SmsCommandSender:
    @staticmethod
    def send(vehicle: Vehicle, command: str):
        command = f'{command}'
        body = {
            'iccid': [vehicle.gps_device.iccid],
            'text': command
        }
        response = requests.post(SMS_SEND_COMMANDS_API_URL, headers=HEADERS, json=body)
        response = response.json()
        resourceURL = response['resourceURL']
        resourceURL = resourceURL.replace('send_smsstatus', 'send_sms/status')
        print(response)
        print(resourceURL)
        response = requests.get(resourceURL, headers=HEADERS)
        return response


