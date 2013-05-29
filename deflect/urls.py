from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns('',
    url(r'^(?P<slug>\w+)/?$', 'deflect.views.redirect', name='redirect'),
)
