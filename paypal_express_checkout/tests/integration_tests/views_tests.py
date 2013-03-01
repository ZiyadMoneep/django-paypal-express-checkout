"""Tests for the views of the ``paypal_express_checkout`` app."""
from mock import Mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from paypal_express_checkout.forms import PayPalFormMixin
from paypal_express_checkout.tests.factories import (
    ItemFactory,
    PaymentTransactionFactory,
)


class PaymentViewTestCaseMixin(ViewTestMixin):
    def should_redirect_to_login_when_anonymous(self):
        """Custom method to overwrite the one from django_libs."""
        url = self.get_url()
        resp = self.client.get(url)
        self.assertRedirects(resp, '{0}?next={1}'.format('/', url))


class DoExpressCheckoutViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``DoExpressCheckoutView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_confirm'

    def get_post_data(self):
        return {
            'token': self.transaction.transaction_id,
            'payerID': 'testpayerID',
        }

    def setUp(self):
        self.user = UserFactory()
        self.transaction = PaymentTransactionFactory(user=self.user)
        self.item = ItemFactory()

        self.paypal_response = {
            'ACK': ['Success'],
            'TOKEN': ['abc123'],
            'PAYMENTINFO_0_TRANSACTIONID': ['abc123']
        }

        self.data = {
            'item': self.item.pk,
            'quantity': 1,
        }

        self.old_call_paypal = PayPalFormMixin.call_paypal
        PayPalFormMixin.call_paypal = Mock(return_value=self.paypal_response)

    def tearDown(self):
        PayPalFormMixin.call_paypal = self.old_call_paypal

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable('post', data=self.get_post_data(), user=self.user)


class PaymentCancelViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentCancelView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_canceled'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class PaymentErrorViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentErrorView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_error'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class PaymentSuccessViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentSuccessView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_success'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class SetExpressCheckoutViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``SetExpressCheckoutView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_checkout'

    def get_post_data(self):
        return {
            'USER': settings.API_USER,
            'PWD': settings.API_PASSWORD,
            'SIGNATURE': settings.API_SIGNATURE,
            'VERSION': '91.0',
            'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
            'METHOD': 'SetExpressCheckout',

            'L_PAYMENTREQUEST_0_NAME0': self.item.name,
            'L_PAYMENTREQUEST_0_DESC0': self.item.description,
            'L_PAYMENTREQUEST_0_AMT0': self.item.value,
            'L_PAYMENTREQUEST_0_QTY0': 1,

            'PAYMENTREQUEST_0_AMT': self.item.value,
            'PAYMENTREQUEST_0_ITEMAMT': self.item.value,
            'RETURNURL': settings.HOSTNAME + reverse(
                'paypal_confirm'),
            'CANCELURL': settings.HOSTNAME + reverse(
                'paypal_canceled')
        }

    def setUp(self):
        self.user = UserFactory()
        self.item = ItemFactory()

        self.paypal_response = {
            'ACK': ['Success'],
            'TOKEN': ['abc123'],
        }

        self.data = {
            'item': self.item.pk,
            'quantity': 1,
        }

        self.old_call_paypal = PayPalFormMixin.call_paypal
        PayPalFormMixin.call_paypal = Mock(return_value=self.paypal_response)

    def tearDown(self):
        PayPalFormMixin.call_paypal = self.old_call_paypal

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable('post', data=self.get_post_data(), user=self.user)
