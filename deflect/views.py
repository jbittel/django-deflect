from __future__ import unicode_literals

import base32_crockford
import logging

from django.db.models import F
from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import RedirectURL
from .utils import add_query_params


logger = logging.getLogger(__name__)


def redirect(request, key):
    """
    Given the short URL key, update the statistics and redirect the
    user to the destination URL, including available Google Analytics
    parameters.
    """
    try:
        id = base32_crockford.decode(key)
    except ValueError as e:
        logger.warning("Error decoding redirect '%s': %s" % (key, e))
        raise Http404

    redirect = get_object_or_404(RedirectURL, pk=id)
    RedirectURL.objects.filter(pk=id).update(hits=F('hits') + 1,
                                             last_used=now())

    # Inject Google campaign parameters; if any of these
    # are not set, they will be ignored
    utm_params = {'utm_source': redirect.key,
                  'utm_campaign': redirect.campaign,
                  'utm_content': redirect.content,
                  'utm_medium': redirect.medium}
    url = add_query_params(redirect.url, utm_params)

    return HttpResponsePermanentRedirect(url)
