try:
    from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
except ImportError:  # pragma: no cover
    from urllib import urlencode
    from urlparse import parse_qsl, urlparse, urlunparse


def add_query_params(url, params):
    """
    Inject additional query parameters into an existing URL. If
    parameters already exist with the same name, they will be
    overwritten. Return the modified URL as a string.
    """
    # Ignore additional parameters with empty values
    params = dict([(k, v) for k, v in params.items() if v])
    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4]))
    query.update(params)
    parts[4] = urlencode(query)
    return urlunparse(parts)
