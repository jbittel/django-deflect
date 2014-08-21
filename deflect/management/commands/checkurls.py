from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.core.management.base import NoArgsCommand
from django.core.urlresolvers import reverse

import requests

from deflect.models import ShortURL
from deflect.compat import gevent

if gevent:
    from gevent.pool import Pool
    from gevent import monkey
    monkey.patch_all(thread=False, select=False)


class Command(NoArgsCommand):
    help = "Validate short URL redirect targets"
    domain = Site.objects.get_current().domain
    message = ''

    def handle_noargs(self, *args, **options):
        def spawn(url, pool=None):
            if pool is not None:
                return pool.spawn(self.validate_url, url)
            return gevent.spawn(self.validate_url, url)

        urls = list(ShortURL.objects.all())

        if gevent:
            size = getattr(settings, 'DEFLECT_ASYNC_CONCURRENCY', None)
            pool = Pool(size) if size else None
            requests = [spawn(u, pool=pool) for u in urls]
            gevent.joinall(requests)
        else:
            for url in urls:
                self.validate_url(url)
        mail_managers('URL report for %s' % self.domain, self.message)

    def validate_url(self, url):
        """
        Validate a given URL. If an exception is raised, append an
        informational text block with the failure details.
        """
        try:
            url.check_status()
        except requests.exceptions.RequestException as e:
            edit_url = 'http://%s%s' % (
                    self.domain, reverse('admin:deflect_shorturl_change', args=(url.id,)))
            self.message += """

Redirect {key} with target {target} returned {error}

Edit this short URL: {edit_url}
""".format(key=url.key, target=url.long_url, error=e, edit_url=edit_url)
