from __future__ import unicode_literals

import base32_crockford
import logging

from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from .models import ShortURL
from .models import ShortURLAlias


logger = logging.getLogger(__name__)


def redirect(request, key):
    """
    Given the short URL key, update the statistics and redirect the
    user to the destination URL.
    """
    try:
        alias = ShortURLAlias.objects.get(alias=key.lower())
        key_id = alias.redirect_id
    except ShortURLAlias.DoesNotExist:
        try:
            key_id = base32_crockford.decode(key)
        except ValueError as e:
            logger.warning("Error decoding redirect: %s" % e)
            raise Http404

    redirect = get_object_or_404(ShortURL, pk=key_id)
    ShortURL.objects.increment_hits(redirect.pk)

    if redirect.is_tracking:
        return HttpResponsePermanentRedirect(redirect.get_redirect_url())
    else:
        return HttpResponseRedirect(redirect.get_redirect_url())
