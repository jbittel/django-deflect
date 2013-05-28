from __future__ import unicode_literals

import unittest

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from .models import RedirectURL


class RedirectURLTests(unittest.TestCase):
    """
    Tests for the RedirectURL model methods.
    """

    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        self.user = User.objects.create_user('testing')
        self.url = RedirectURL.objects.create(id=1,
                                              url='http://www.example.com',
                                              user=self.user)

    def tearDown(self):
        """
        Remove all user and model instances.
        """
        RedirectURL.objects.all().delete()
        User.objects.all().delete()

    def test_url_path(self):
        """
        The URL path should be equal to just the model's calculated
        short URL value.
        """
        self.assertEqual(self.url.url_path, '1')

    def test_absolute_url(self):
        """
        The absolute URL should be equal to the model's short URL
        path component.
        """
        self.assertEqual(self.url.get_absolute_url(), '/1')

    def test_short_url(self):
        """
        The short URL should be equal to the model's complete URL,
        including the scheme, domain and path.
        """
        self.assertEqual(self.url.short_url(), 'http://example.com/1')

    def test_qr_code(self):
        """
        The QR code should return an HTML img tag containing an
        inline base64 PNG image.
        """
        self.assertIn('<img src="data:image/png;base64,', self.url.qr_code())
