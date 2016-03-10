# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class PaymentAPITest(TestCase):

    def setUp(self):
        self.data = {'code': 'TODO'}
        self.notification_url = reverse('fun-payment-api:payment-notification')

    def test_api_response_loads(self):
        response = self.client.post(self.notification_url, self.data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response_data)
