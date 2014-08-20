from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.core.management.base import NoArgsCommand
from django.core.urlresolvers import reverse

import requests

from deflect.models import ShortURL


class Command(NoArgsCommand):
    help = "Validate short URL redirect targets"
    domain = Site.objects.get_current().domain

    def handle_noargs(self, *args, **options):
        message = ''
        for url in ShortURL.objects.all():
            try:
                url.check_status()
            except requests.exceptions.RequestException as e:
                message += self.url_exception_text(url, e)
        mail_managers('URL report for %s' % self.domain, message)

    def url_exception_text(self, url, exception):
        """Return text block for a URL exception."""
        base = 'http://%s' % self.domain
        return """

Redirect {key} with target {target} returned {error}

Edit this short URL: {edit}
""".format(key=url.key, target=url.long_url, error=exception,
        edit=base + reverse('admin:deflect_shorturl_change', args=(url.id,)))
