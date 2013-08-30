from __future__ import unicode_literals

from django.test import TestCase
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

import base32_crockford

from ..models import ShortURL
from ..models import ShortURLAlias


class ShortURLTests(TestCase):
    """
    Tests for the ShortURL model methods.
    """

    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        self.user = User.objects.create_user('testing')
        self.shorturl = ShortURL.objects.create(long_url='http://www.example.com',
                                                creator=self.user)
        self.alias = ShortURLAlias.objects.create(redirect=self.shorturl,
                                                  alias='test')
        self.key = base32_crockford.encode(self.shorturl.pk)

    def test_key(self):
        """
        The key should be equal to just the model's calculated short
        URL value.
        """
        self.assertEqual(self.shorturl.key, self.key)

    def test_absolute_url(self):
        """
        The absolute URL should be equal to the model's short URL
        path component.
        """
        self.assertEqual(self.shorturl.get_absolute_url(), '/' + self.key)

    def test_alias_url(self):
        """
        The alias URL should be equal to the short URL alias, when
        present.
        """
        self.assertEqual(self.shorturl.get_alias_url(), '/test')

    def test_short_url(self):
        """
        The short URL should be equal to the model's complete URL,
        including the scheme, domain and path.
        """
        self.assertEqual(self.shorturl.short_url(), 'http://example.com/test')
        self.assertEqual(self.shorturl.short_url(alias=False), 'http://example.com/' + self.key)

    def test_qr_code(self):
        """
        The QR code should return an HTML img tag containing an
        inline base64 PNG image.
        """
        self.assertIn('<img src="data:image/png;base64,', self.shorturl.qr_code())
