from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.utils import unittest
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from ..models import RedirectURL


class RedirectViewTests(TransactionTestCase):
    """
    Tests for the redirect view.
    """
    reset_sequences = True

    def assertInHeader(self, response, text, header):
        self.assertIn(text, response._headers[header][1])

    def assertRedirectsNoFollow(self, response, expected_url, status_code=301):
        self.assertInHeader(response, expected_url, 'location')
        self.assertEqual(response.status_code, status_code)

    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        self.user = User.objects.create_user('testing')
        RedirectURL.objects.create(url='http://www.example.com',
                                   creator=self.user,
                                   campaign='example',
                                   medium='email',
                                   content='test')

    def test_redirect(self):
        """
        A valid key should return a permanent redirect to the target
        URL with all parameters included.
        """
        response = self.client.get(reverse('deflect-redirect', args=[1]))
        self.assertRedirectsNoFollow(response, 'http://www.example.com')
        self.assertInHeader(response, 'utm_source=1', 'location')
        self.assertInHeader(response, 'utm_campaign=example', 'location')
        self.assertInHeader(response, 'utm_medium=email', 'location')
        self.assertInHeader(response, 'utm_content=test', 'location')
