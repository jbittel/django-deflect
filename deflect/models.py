from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

import base32_crockford
import requests

from .compat import user_model
from .utils import add_query_params
from .utils import get_qr_code_img


class ShortURLManager(models.Manager):
    def increment_hits(self, id):
        """
        Increment a ``ShortURL``s hits by one, and set the last
        used timestamp to the current time.
        """
        self.filter(pk=id).update(hits=F('hits') + 1, last_used=now())

    def get_unique_list(self, field):
        """
        Get a list of non-blank, unique values from a specified
        field.
        """
        blank = {'%s__exact' % field: ''}
        return self.exclude(**blank).values_list(field, flat=True).distinct()


@python_2_unicode_compatible
class ShortURL(models.Model):
    """
    A ``ShortURL`` represents a redirection mapping between a short
    URL and the full destination URL. Several additional values are
    stored with related data and usage statistics.
    """
    campaign = models.CharField(_('campaign'), max_length=64, blank=True,
                                help_text=_('The individual campaign name, slogan, promo code, etc. for a product'))
    content = models.CharField(_('content'), max_length=64, blank=True,
                               help_text=_('Used to differentiate similar content, or links within the same ad'))
    created = models.DateTimeField(_('created'), editable=False)
    creator = models.ForeignKey(user_model, verbose_name=_('creator'), editable=False)
    description = models.TextField(_('description'), blank=True)
    hits = models.IntegerField(_('hits'), default=0, editable=False)
    last_used = models.DateTimeField(_('last used'), editable=False, blank=True, null=True)
    long_url = models.URLField(_('long URL'),
                               help_text=_('The target URL to which the short URL redirects'))
    medium = models.CharField(_('medium'), max_length=64, blank=True,
                              help_text=_('The advertising or marketing medium, e.g.: postcard, banner, email newsletter'))
    is_tracking = models.BooleanField(_('is this a tracking URL?'), default=True,
                                      help_text=_('Determine whether or not to redirect with tracking parameters'))

    objects = ShortURLManager()

    class Meta:
        verbose_name = _('short URL')
        verbose_name_plural = _('short URLs')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        super(ShortURL, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('deflect-redirect', args=[self.key])

    def get_alias_url(self):
        try:
            return reverse('deflect-redirect', args=[self.shorturlalias.alias])
        except ShortURLAlias.DoesNotExist:
            return self.get_absolute_url()

    def get_redirect_url(self, params={}):
        """
        Return the complete redirect URL. If it is a tracking URL, inject
        available Google campaign parameters into the destination URL.
        """
        if self.is_tracking:
            params['utm_source'] = self.key
            params['utm_campaign'] = self.campaign.lower()
            params['utm_content'] = self.content.lower()
            params['utm_medium'] = self.medium.lower()
            if getattr(settings, 'DEFLECT_NOOVERRIDE', False):
                params['utm_nooverride'] = '1'
        return add_query_params(self.long_url, params)
    get_redirect_url.short_description = 'redirect URL'

    @property
    def key(self):
        return base32_crockford.encode(self.pk)

    def short_url(self, alias=True):
        """
        Return the complete short URL for the current redirect. If
        ``alias`` is ``True``, use the URL alias when available.
        """
        base = 'http://%s' % Site.objects.get_current().domain
        if alias:
            return base + self.get_alias_url()
        return base + self.get_absolute_url()
    short_url.short_description = 'short URL'

    def qr_code(self):
        """
        Return a HTML img tag with an inline representation of the
        short URL as a QR code. The absolute URL is used for the URL.
        """
        return get_qr_code_img(self.short_url(alias=False))
    qr_code.allow_tags = True
    qr_code.short_description = 'QR code'

    def check_status(self):
        """
        Validate the destination URL, checking for connection errors
        or invalid HTTP status codes.
        """
        r = requests.head(self.long_url, allow_redirects=True, timeout=3.0)
        r.raise_for_status()


@python_2_unicode_compatible
class ShortURLAlias(models.Model):
    """
    A ``ShortURLAlias`` is an optional, custom alias for a ``ShortURL``
    that can be used in place of the generated key.
    """
    redirect = models.OneToOneField(ShortURL)
    alias = models.CharField(_('alias'), max_length=16, unique=True,
                             help_text=_('A custom alias for the short URL'))

    class Meta:
        verbose_name = _('alias')
        verbose_name_plural = _('aliases')

    def __str__(self):
        return self.alias

    def save(self, *args, **kwargs):
        if self.alias:
            self.alias = self.alias.lower()
        super(ShortURLAlias, self).save(*args, **kwargs)
