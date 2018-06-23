"""
Tests for django-registration's built-in views.

"""

from django.core import signing
from django.test import RequestFactory, override_settings
from django.urls import reverse

from django_registration.backends.hmac.views import (
    REGISTRATION_SALT, RegistrationView
)

from .base import RegistrationTestCase


@override_settings(ROOT_URLCONF='tests.urls')
class ActivationViewTests(RegistrationTestCase):
    """
    Tests for aspects of the activation view not currently exercised
    by any built-in workflow.

    """
    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation(self):
        """
        Activation of an account functions properly when using a
        string URL as the success redirect.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[self.user_model.USERNAME_FIELD],
            salt=REGISTRATION_SALT
        )

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )
        self.assertRedirects(resp, '/activate/complete/')


@override_settings(ROOT_URLCONF='django_registration.backends.hmac.urls')
class HMACRegistrationViewTest(RegistrationTestCase):
    """Test for registration.backends.hmac.views.RegistrationView directly
    """
    @override_settings(SECURE_PROXY_SSL_HEADER=None)
    def test_default_scheme(self):
        view = RegistrationView()
        factory = RequestFactory()
        view.request = factory.get('')
        context = view.get_email_context('')
        self.assertEqual(context['scheme'], 'http')

    @override_settings(
        SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_not_secure_scheme(self):
        view = RegistrationView()
        factory = RequestFactory()
        view.request = factory.get('', HTTP_X_FORWARDED_PROTO='http')
        context = view.get_email_context('')
        self.assertEqual(context['scheme'], 'http')

    @override_settings(
        SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_secure_scheme(self):
        view = RegistrationView()
        factory = RequestFactory()
        view.request = factory.get('', HTTP_X_FORWARDED_PROTO='https')
        context = view.get_email_context('')
        self.assertEqual(context['scheme'], 'https')
