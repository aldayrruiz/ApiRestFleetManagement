from rest_framework.exceptions import ValidationError
from dateutil import parser
from utils.api.validators import is_valid_uuid


def query_bool(request, query) -> bool:
    """
    The query must be a boolean like True, 'True', 'true'
    :param request:
    :param query: query name (str)
    :return: boolean value given the query name.
    """
    return request.query_params.get(query) in [True, 'true', 'True']


def query_date(request, query):
    if query not in request.query_params:
        return None
    return parser.parse(request.query_params.get(query))


def query_str(request, query: str, required=False):
    result = request.query_params.get(query)
    if required and result in [None, '', 'undefined']:
        raise ValidationError(f'Query {query} is required.')
    return result


def query_uuid(request, query, required=False):
    val = query_str(request, query)
    is_valid = is_valid_uuid(val)

    if not required and val in [None, '', 'undefined']:
        return None

    if required and val in [None, '', 'undefined']:
        raise ValidationError(f'Query {query} is required.')

    if required and not is_valid:
        raise ValidationError(f'Query {query} is not an UUID v4.')

    return val
