# gevent is optional, and allows for asynchronous requests. If it is
# not present, synchronous requests will be sent.
try:
    import gevent
except ImportError:
    gevent = None


# Support both Python 2 and Python 3 locations for urllib imports.
try:
    from urllib.parse import parse_qsl
    from urllib.parse import urlencode
    from urllib.parse import urlparse
    from urllib.parse import urlunparse
except ImportError:  # pragma: no cover
    from urllib import urlencode
    from urlparse import parse_qsl
    from urlparse import urlparse
    from urlparse import urlunparse
