from __future__ import unicode_literals

import base32_crockford

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User


@python_2_unicode_compatible
class RedirectURL(models.Model):
    """
    """
    campaign = models.CharField(_('campaign'), max_length=64, blank=True,
                                help_text=_('The individual campaign name, slogan, promo code, etc. for a product.'))
    content = models.CharField(_('content'), max_length=64, blank=True,
                               help_text=_('Used to differentiate similar content, or links within the same ad.'))
    created = models.DateTimeField(_('created'), auto_now_add=True, editable=False)
    description = models.TextField(_('description'), blank=True)
    hits = models.IntegerField(default=0, editable=False)
    last_used = models.DateTimeField(_('last used'), editable=False, blank=True, null=True)
    medium = models.CharField(_('medium'), max_length=64, blank=True,
                              help_text=_('The advertising or marketing medium, e.g.: cpc, banner, email newsletter.'))
    url = models.URLField(_('target url'), help_text=_('The full destination URL redirected to from the short URL.'))
    user = models.ForeignKey(User, verbose_name=_('user'), editable=False)

    def __str__(self):
        return self.url

    @property
    def short_url(self):
        """
        Return the encoded representation of the current model's
        primary key field.
        """
        return base32_crockford.encode(self.pk)
