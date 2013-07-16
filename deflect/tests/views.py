from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

import base32_crockford

from ..models import RedirectURL


class RedirectViewTests(TestCase):
    """
    Tests for the redirect view.
    """

    def assertInHeader(self, response, text, header):
        """
        Check that given text is contained within a specified
        response header field.
        """
        self.assertIn(text, response._headers[header][1])

    def assertRedirectsNoFollow(self, response, expected_url, status_code=301):
        """
        Check that a given response contains a Location header
        redirect to the expected URL. Differs from assertRedirects
        in that it does not attempt to follow the redirect URL.
        """
        self.assertInHeader(response, expected_url, 'location')
        self.assertEqual(response.status_code, status_code)

    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        self.user = User.objects.create_user('testing')
        self.r = RedirectURL.objects.create(url='http://www.example.com',
                                            creator=self.user,
                                            campaign='example',
                                            medium='email',
                                            content='test')
        self.key = base32_crockford.encode(self.r.pk)

    def test_redirect(self):
        """
        A valid key should return a permanent redirect to the target
        URL with all parameters included.
        """
        response = self.client.get(reverse('deflect-redirect', args=[self.key]))
        self.assertRedirectsNoFollow(response, 'http://www.example.com')
        self.assertInHeader(response, 'utm_source=' + self.key, 'location')
        self.assertInHeader(response, 'utm_campaign=example', 'location')
        self.assertInHeader(response, 'utm_medium=email', 'location')
        self.assertInHeader(response, 'utm_content=test', 'location')
