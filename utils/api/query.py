from rest_framework.exceptions import ValidationError

from utils.api.validators import is_valid_uuid
from utils.dates import get_date_from_str_utc


def query_bool(request, query) -> bool:
    """
    The query must be a boolean like True, 'True', 'true'
    :param request:
    :param query: query name (str)
    :return: boolean value given the query name.
    """
    return request.query_params.get(query) in [True, 'true', 'True']


def query_date(request, query):
    return get_date_from_str_utc(request.query_params.get(query))


def query_str(request, query: str, required=False):
    result = request.query_params.get(query)
    if required and result in [None, '', 'undefined']:
        raise ValidationError(f'Query {query} is required.')
    return result


def query_uuid(request, query):
    val = query_str(request, query)
    is_valid = is_valid_uuid(val)
    if not is_valid:
        raise ValidationError(f'Query {query} is not an UUID v4.')
    return val
