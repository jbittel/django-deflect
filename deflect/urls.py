from django.conf.urls import url

from .views import redirect


app_name = 'deflect'

urlpatterns = [
    url(r'^(?P<key>[a-zA-Z0-9-]+)$', redirect, name='redirect'),
]
