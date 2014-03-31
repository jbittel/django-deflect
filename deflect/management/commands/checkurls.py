from django.contrib.sites.models import Site
from django.core.management.base import NoArgsCommand
from django.core.urlresolvers import reverse

import requests

from deflect.models import ShortURL


class Command(NoArgsCommand):
    help = "Validate short URL redirect targets"

    def handle_noargs(self, *args, **options):
        for url in ShortURL.objects.all():
            try:
                url.check_status()
            except requests.exceptions.RequestException as e:
                print self.bad_redirect_text(url, e)

    def bad_redirect_text(self, url, exception):
        """
        Return informational text for a URL that raised an
        exception.
        """
        base = 'http://%s' % Site.objects.get_current().domain
        return """
Redirect {key} with target {target} returns {error}

Edit this short URL: {edit}
""".format(key=url.key, target=url.long_url, error=exception,
        edit=base + reverse('admin:deflect_shorturl_change', args=(url.id,)))
