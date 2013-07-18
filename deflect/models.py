from __future__ import unicode_literals

import base64
from cStringIO import StringIO

import base32_crockford
import qrcode

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User


@python_2_unicode_compatible
class RedirectURL(models.Model):
    """
    A ``RedirectURL`` represents a redirection mapping between a short
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
    long_url = models.URLField(_('long url'),
                               help_text=_('The target URL to which the short URL redirects'))
    medium = models.CharField(_('medium'), max_length=64, blank=True,
                              help_text=_('The advertising or marketing medium, e.g.: postcard, banner, email newsletter'))

    class Meta:
        verbose_name = _('Redirect URL')
        verbose_name_plural = _('Redirect URLs')

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        super(RedirectURL, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('deflect-redirect', args=[self.key])

    @property
    def key(self):
        return base32_crockford.encode(self.pk)

    def short_url(self):
        """
        Return the complete short URL for the current redirect.
        """
        url_base = 'http://%s' % Site.objects.get_current().domain
        return url_base + self.get_absolute_url()

    def qr_code(self):
        """
        Return an HTML img tag containing an inline base64 encoded
        representation of the short URL as a QR code.
        """
        png_stream = StringIO()
        img = qrcode.make(self.short_url())
        img.save(png_stream)
        png_base64 = base64.b64encode(png_stream.getvalue())
        png_stream.close()
        return '<img src="data:image/png;base64,%s" />' % png_base64
    qr_code.allow_tags = True


@python_2_unicode_compatible
class CustomURL(models.Model):
    """
    A ``CustomURL`` is an optional alias for a ``RedirectURL`` that
    can be used in place of the generated key. It is prepended with
    a configured prefix to differentiate an alias from a generated
    key.
    """
    alias_prefix = getattr(settings, 'DEFLECT_ALIAS_PREFIX', '')

    redirect = models.OneToOneField(RedirectURL)
    alias = models.CharField(_('alias'), max_length=8, blank=True,
                             help_text=_('An alias for the generated short URL; will be prefixed with "%s"' % alias_prefix))

    def __str__(self):
        return alias_prefix + self.alias
