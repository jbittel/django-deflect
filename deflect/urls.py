from django.conf.urls import url

from .views import redirect


urlpatterns = [
    url(r'^(?P<key>[a-zA-Z0-9-]+)$', redirect, name='deflect-redirect'),
]
