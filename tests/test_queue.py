# -*- coding: utf-8 -*-

import settings
from queue import XQueuePullManager
from mock import patch


def test_pop_good():
    auth_basic = (settings.QUEUE_AUTH_USER, settings.QUEUE_AUTH_PASS)
    auth_xqueue = (settings.QUEUE_USER, settings.QUEUE_PASS)
    with patch.object(XQueuePullManager, '_request') as mock:
        mock.return_value = {}
        manager = XQueuePullManager(
            settings.QUEUE_URL,
            settings.QUEUE_NAME,
            auth_basic,
            auth_xqueue,
        )
