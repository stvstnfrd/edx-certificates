# -*- coding: utf-8 -*-
import requests
import responses
import re
import unittest

import settings
from mock import patch
from queue import XQueuePullManager


class QueueTest(unittest.TestCase):

    def setUp(self):
        auth_basic = (settings.QUEUE_AUTH_USER, settings.QUEUE_AUTH_PASS)
        auth_xqueue = (settings.QUEUE_USER, settings.QUEUE_PASS)
        self.manager = XQueuePullManager(
            'http://example.com',
            settings.QUEUE_NAME,
            auth_basic,
            auth_xqueue,
        )

    def test_init(self):
        pass

    def test_init_fail_auth_basic(self):
        """
        auth_basic = (settings.QUEUE_AUTH_USER, settings.QUEUE_AUTH_PASS)
        auth_xqueue = (settings.QUEUE_USER, settings.QUEUE_PASS)
        manager = XQueuePullManager(
            'http://example.com',
            settings.QUEUE_NAME,
            auth_basic,
            auth_xqueue,
        )
        """
        pass

    def test_init_fail_auth_xqueue(self):
        pass

    def test_put(self):
        """
        xqueue_reply = {
            'xqueue_header': json.dumps(xqueue_header),
            'xqueue_body': json.dumps({
                'action': action,
                'download_uuid': download_uuid,
                'verify_uuid': verify_uuid,
                'username': username,
                'course_id': course_id,
                'url': download_url,
            }),
        }
        self.manager.put(xqueue_reply)
        """
        pass

    def test_put_fail(self):
        """
        self.manager = get_invalid_manager()
        with self.assertRaises(ExceptionTypeHere):
            self.manager.put({
                # pass reply here
            })
        """
        pass

    def test_pop(self):
        """
        certdata = self.manager.pop()
        """
        pass

    def test_pop_fail(self):
        """
        self.manager = get_invalid_manager()
        with self.assertRaises(ExceptionTypeHere):
            self.manager.pop()
        """
        pass

    def test_str(self):
        """
        Test string and unicode representations are equal to the base URL
        """
        string_str = str(self.manager)
        string_unicode = unicode(self.manager)
        self.assertEquals(string_str, string_unicode)

    def test_len(self):
        pass

    def test_len_fail(self):
        pass

"""
        @responses.activate
        def run():
            responses.add(
                responses.POST,
                re.compile(r'http://example\.com/.*'),
                body="{
                    "return_code": 0,
                    "content": "value"
                }",
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
"""
