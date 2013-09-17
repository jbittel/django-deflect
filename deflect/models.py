from __future__ import unicode_literals

import base32_crockford

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from .utils import add_query_params
from .utils import get_qr_code_img


class ShortURLManager(models.Manager):
    def increment_hits(self, id):
        """
        Increment a ``ShortURL``s hits by one, and set the last
        used timestamp to the current time.
        """
        self.filter(pk=id).update(hits=F('hits') + 1, last_used=now())


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
    creator = models.ForeignKey(User, verbose_name=_('creator'), editable=False)
    description = models.TextField(_('description'), blank=True)
    hits = models.IntegerField(_('hits'), default=0, editable=False)
    last_used = models.DateTimeField(_('last used'), editable=False, blank=True, null=True)
    long_url = models.URLField(_('long URL'),
                               help_text=_('The target URL to which the short URL redirects'))
    medium = models.CharField(_('medium'), max_length=64, blank=True,
                              help_text=_('The advertising or marketing medium, e.g.: postcard, banner, email newsletter'))

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

    def get_tracking_url(self):
        """
        Build the complete tracking URL by injecting Google campaign
        parameters into the destination URL.
        """
        utm_params = {'utm_source': self.key,
                      'utm_campaign': self.campaign.lower(),
                      'utm_content': self.content.lower(),
                      'utm_medium': self.medium.lower()}
        return add_query_params(self.long_url, utm_params)
    get_tracking_url.short_description = 'tracking URL'

    @property
    def key(self):
        return base32_crockford.encode(self.pk)

    def short_url(self, alias=True):
        """
        Return the complete short URL for the current redirect. If
        ``alias`` is ``True``, use the URL alias when available.
        """
        url_base = 'http://%s' % Site.objects.get_current().domain
        if not alias:
            return url_base + self.get_absolute_url()
        return url_base + self.get_alias_url()
    short_url.short_description = 'short URL'

    def qr_code(self):
        """
        Return a HTML img tag with an inline representation of the
        short URL as a QR code. The absolute URL is used for the URL.
        """
        return get_qr_code_img(self.short_url(alias=False))
    qr_code.allow_tags = True
    qr_code.short_description = 'QR code'


@python_2_unicode_compatible
class ShortURLAlias(models.Model):
    """
    A ``ShortURLAlias`` is an optional, custom alias for a ``ShortURL``
    that can be used in place of the generated key.
    """
    redirect = models.OneToOneField(ShortURL)
    alias = models.CharField(_('alias'), max_length=16, blank=True, unique=True,
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
