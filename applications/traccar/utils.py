import json

import requests
from decouple import config

base_url = config('TRACCAR_URL') + ':' + config('TRACCAR_PORT') + '/api/'
auth = (config('TRACCAR_USER'), config('TRACCAR_PASSWORD'))


def get(target, data):
    url = base_url + target
    return requests.get(url, auth=auth)


def post(target, data):
    url = base_url + target
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps(data)
    return requests.post(url, headers=headers, data=payload, auth=auth)


def put(target, data):
    url = base_url + target
    return requests.put(url, data=data, auth=auth)
