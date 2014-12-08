import base64
from cStringIO import StringIO

import qrcode

from .compat import parse_qsl
from .compat import urlencode
from .compat import urlparse
from .compat import urlunparse


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


def get_qr_code_img(url):
    """
    Return an HTML img tag containing an inline base64 encoded
    representation of the provided URL as a QR code.
    """
    png_stream = StringIO()
    img = qrcode.make(url)
    img.save(png_stream)
    png_base64 = base64.b64encode(png_stream.getvalue())
    png_stream.close()
    return '<img src="data:image/png;base64,%s" />' % png_base64
