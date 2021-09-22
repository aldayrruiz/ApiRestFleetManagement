from utils.dates import get_date_from_str_utc


def query_bool(request, query):
    """
    The query must be a boolean like True, 'True', 'true'
    :param request:
    :param query: query name (str)
    :return: boolean value given the query name.
    """
    return request.query_params.get(query) in [True, 'true', 'True']


def query_date(request, query):
    return get_date_from_str_utc(request.query_params.get(query))


def query_str(request, query):
    return request.query_params.get(query)
