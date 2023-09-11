from rest_framework.exceptions import ValidationError
from dateutil import parser
from utils.api.validators import is_valid_uuid


INVALID_STRINGS = [None, '', 'undefined']

def query_bool(request, query) -> bool:
    """
    The query must be a boolean like True, 'True', 'true'
    :param request:
    :param query: query name (str)
    :return: boolean value given the query name.
    """
    return request.query_params.get(query) in [True, 'true', 'True']


def query_date(request, query, required=False):
    if query not in request.query_params:
        return None
    value = request.query_params.get(query)

    if not required and value in INVALID_STRINGS:
        return None

    if required and value in INVALID_STRINGS:
        raise ValidationError(f'Query {query} is required.')
    return parser.parse(value)


def query_str(request, query: str, required=False):
    value = request.query_params.get(query)

    if required and value in INVALID_STRINGS:
        raise ValidationError(f'Query {query} is required.')
    if not required and value in INVALID_STRINGS:
        return None
    return value


def query_uuid(request, query, required=False):
    value = query_str(request, query)
    is_valid = is_valid_uuid(value)

    if not required and value in INVALID_STRINGS:
        return None

    if required and value in INVALID_STRINGS:
        raise ValidationError(f'Query {query} is required.')

    if required and not is_valid:
        raise ValidationError(f'Query {query} is not an UUID v4.')

    return value

