import json

import requests
from decouple import config

base_url = '{}:{}/api/'.format(config('TRACCAR_URL'), config('TRACCAR_PORT'))
auth = (config('TRACCAR_USER'), config('TRACCAR_PASSWORD'))

headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def get(target, params):
    url = base_url + target
    return requests.get(url, headers=headers, params=params, auth=auth)


def post(target, data):
    url = base_url + target
    payload = json.dumps(data)
    return requests.post(url, headers=headers, data=payload, auth=auth)


def put(target, data):
    url = '{}{}/{}'.format(base_url, target, data['id'])
    payload = json.dumps(data)
    return requests.put(url, headers=headers, data=payload, auth=auth)

