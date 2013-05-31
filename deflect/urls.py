from django.conf.urls import patterns
from django.conf.urls import url

from .views import redirect


urlpatterns = patterns('',
    url(r'^(?P<slug>[a-zA-Z0-9]+)$', redirect, name='deflect-redirect'),
)
