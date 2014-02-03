from django.conf import settings


__all__ = ['user_model', 'get_user_model']


# Django >= 1.5 uses AUTH_USER_MODEL to specify the currently active
# User model. Previous versions of Django do not have this setting
# and use the built-in User model.
#
# This is not needed when support for Django 1.4 is dropped.
user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


# In Django >= 1.5 get_user_model() returns the currently active
# User model. Previous versions of Django have no concept of custom
# User models and reference User directly.
#
# This is not needed when support for Django 1.4 is dropped.
try:
    from django.contrib.auth import get_user_model
except ImportError:  # pragma: no cover
    from django.contrib.auth.models import User
    get_user_model = lambda: User
