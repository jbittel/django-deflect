from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

import base32_crockford

from ..models import ShortURL
from ..models import ShortURLAlias


class DeflectTests(TestCase):
    """
    Base inherited class with helper methods.
    """
    def assertInHeader(self, response, text, header):
        """
        Check that given text is contained within a specified
        response header field.
        """
        self.assertIn(text, response._headers[header][1])

    def assertRedirectsNoFollow(self, response, expected_url, status_code=301):
        """
        Check that a given response contains a Location header and
        redirects to the expected URL. Differs from assertRedirects
        in that it does not attempt to follow the URL but merely
        checks that the expected Location header is present.
        """
        self.assertInHeader(response, expected_url, 'location')
        self.assertEqual(response.status_code, status_code)


class RedirectViewTests(DeflectTests):
    """
    Tests for the redirect view.
    """
    def setUp(self):
        """
        Create a user and model instance to test against.
        """
        user = get_user_model()
        self.user = user.objects.create_user('testing')
        self.shorturl = ShortURL.objects.create(long_url='http://www.example.com',
                                                creator=self.user,
                                                campaign='Example',
                                                medium='Email',
                                                content='Test')
        self.shorturl2 = ShortURL.objects.create(long_url='http://www.example.com',
                                                 creator=self.user,
                                                 is_tracking=False)
        self.alias = ShortURLAlias.objects.create(redirect=self.shorturl,
                                                  alias='test')
        self.key = base32_crockford.encode(self.shorturl.pk)
        self.invalid_key = base32_crockford.encode(self.shorturl.pk + 2)

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

    def test_redirect_params(self):
        """
        A redirect should include any query parameters provided to the
        short URL.
        """
        url = reverse('deflect-redirect', args=[self.key]) + '?test=param'
        response = self.client.get(url)
        self.assertRedirectsNoFollow(response, 'http://www.example.com')
        self.assertInHeader(response, 'test=param', 'location')

    def test_temporary_redirect(self):
        """
        A non-tracking redirect should return a temporary redirect to
        the target URL.
        """
        key = base32_crockford.encode(self.shorturl2.pk)
        response = self.client.get(reverse('deflect-redirect', args=[key]))
        self.assertRedirectsNoFollow(response, 'http://www.example.com',
                                     status_code=302)

    def test_alias(self):
        """
        A valid alias should return a permanent redirect to the target
        URL with all parameters included.
        """
        response = self.client.get(reverse('deflect-redirect', args=['test']))
        self.assertRedirectsNoFollow(response, 'http://www.example.com')
        self.assertInHeader(response, 'utm_source=' + self.key, 'location')
        self.assertInHeader(response, 'utm_campaign=example', 'location')
        self.assertInHeader(response, 'utm_medium=email', 'location')
        self.assertInHeader(response, 'utm_content=test', 'location')

    def test_invalid_key(self):
        """
        An invalid key should return a 404 status.
        """
        response = self.client.get(reverse('deflect-redirect', args=[self.invalid_key]))
        self.assertEqual(response.status_code, 404)

    def test_invalid_decode(self):
        """
        An invalid decoding error should return a 404 status.
        """
        response = self.client.get(reverse('deflect-redirect', args=['u']))
        self.assertEqual(response.status_code, 404)

    @override_settings(DEFLECT_NOOVERRIDE=True)
    def test_nooverride(self):
        """
        When ``DEFLECT_NOOVERRIDE`` is enabled, the appropriate
        utm parameter should be included in the redirect.
        """
        response = self.client.get(reverse('deflect-redirect', args=[self.key]))
        self.assertInHeader(response, 'utm_nooverride=1', 'location')
