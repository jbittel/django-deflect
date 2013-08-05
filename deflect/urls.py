from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from .views import alias
from .views import redirect


urlpatterns = patterns('',
    url(r'^(?P<key>[a-zA-Z0-9]+)$', redirect, name='deflect-redirect'),
)

alias_prefix = getattr(settings, 'DEFLECT_ALIAS_PREFIX', '')
if alias_prefix:
    urlpatterns += patterns('',
        url(r'^%s(?P<key>[a-zA-Z0-9]+)$' % alias_prefix, alias,
            name='deflect-alias'),
    )
