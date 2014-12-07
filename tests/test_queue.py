# -*- coding: utf-8 -*-
import requests
import responses
import re

import settings
import unittest
from mock import patch
from queue import XQueuePullManager

url_re = re.compile(r'http://example.com/.*')


class QueueTest(unittest.TestCase):

    def setUp(self):
        """
        with patch.object(XQueuePullManager, '_request') as mock:
            mock.return_value = {}
            self.manager = XQueuePullManager(
                'https://example.com/xqueue',
                settings.QUEUE_NAME,
                auth_basic,
                auth_xqueue,
            )
        """
        @responses.activate
        def run():
            responses.add(
                responses.POST,
                re.compile(r'http://example\.com/.*'),
                body="""{
                    "return_code": 0,
                    "content": "value"
                }""",
                content_type='application/json',
                status=200,
            )
            auth_basic = (settings.QUEUE_AUTH_USER, settings.QUEUE_AUTH_PASS)
            auth_xqueue = (settings.QUEUE_USER, settings.QUEUE_PASS)
            self.manager = XQueuePullManager(
                'http://example.com',
                settings.QUEUE_NAME,
                auth_basic,
                auth_xqueue,
            )
        run()

    def test_init(self):
        pass

    def test_init_fail_auth_basic(self):
        pass

    def test_init_fail_auth_xqueue(self):
        pass

    def test_put(self):
        pass

    def test_put_fail(self):
        pass

    def test_pop(self):
        pass

    def test_pop_fail(self):
        pass

    def test_str(self):
        pass

    def test_len(self):
        pass

    def test_len_fail(self):
        pass
