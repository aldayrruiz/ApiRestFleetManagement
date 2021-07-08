import json

import requests
from decouple import config

base_url = '{}:{}/api/'.format(config('TRACCAR_URL'), config('TRACCAR_PORT'))
auth = (config('TRACCAR_USER'), config('TRACCAR_PASSWORD'))

headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def get(target, params, pk=None):
    url = _get_url(target, pk)
    return requests.get(url, headers=headers, params=params, auth=auth)


def post(target, data):
    url = base_url + target
    payload = json.dumps(data)
    return requests.post(url, headers=headers, data=payload, auth=auth)


def put(target, data):
    url = '{}{}/{}'.format(base_url, target, data['id'])
    payload = json.dumps(data)
    return requests.put(url, headers=headers, data=payload, auth=auth)


def delete(target, pk):
    url = _get_url(target, pk)
    return requests.delete(url, headers=headers, auth=auth)


def _get_url(target, pk=None):
    if pk is None:
        return '{}{}'.format(base_url, target)
    else:
        return '{}{}/{}'.format(base_url, target, pk)
