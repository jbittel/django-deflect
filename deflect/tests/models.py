from __future__ import unicode_literals

from django.test import TransactionTestCase
from django.utils import unittest
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from ..models import RedirectURL


class RedirectURLTests(TransactionTestCase):
    """
    Tests for the RedirectURL model methods.
    """
    reset_sequences = True

    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        self.user = User.objects.create_user('testing')
        self.url = RedirectURL.objects.create(url='http://www.example.com',
                                              creator=self.user)

    def test_slug(self):
        """
        The slug should be equal to just the model's calculated short
        URL value.
        """
        self.assertEqual(self.url.slug, '1')

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
