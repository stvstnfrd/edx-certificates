"""
XQueue management wrapper
"""
# TODO: rename this file, get rid of leading capital
import json

import logging
import requests
from requests.exceptions import ConnectionError, Timeout

LOG = logging.getLogger(__name__)

# TODO: standardize naming/formatting
ERROR_CONNECT = "Unable to connect to queue: %s"
ERROR_GET = "Unable to get submission from queue: %s"
ERROR_LEN = "Unable to get queue length: %s"
ERROR_PARSE = "Unable to parse queue message: %s response: %s"
ERROR_POST_RESPONSE = "Connection error posting response to the LMS: %s"
ERROR_VALIDATE = "Invalid return code ({0}): {1}"
MESSAGE_GET_RESPONSE = 'response from get_submission: %s'
MESSAGE_RESPONSE = 'Response: %s'


class InvalidReturnCode(Exception):
    """
    Raise when reponse contains invalid return_code
    """
    pass


# TODO: make this private
def validate(response):
    """
    Check for a valid return code in XQueue response

    :param response: The server response
    :type response: dict
    """
    if response['return_code'] != 0:
        LOG.critical(MESSAGE_RESPONSE, response)
        # LOG.critical("response: %s", response.text)
        raise InvalidReturnCode(ERROR_VALIDATE.format(
            response['return_code'],
            str(response),
        ))


# TODO: rename class
class XQueuePullManager(object):
    """
    Provide an interface to the XQueue server
    """

    def __init__(self, url, name, auth_basic, auth_xqueue):
        """
        Initialize a new XQueuePullManager

        :param url: The base URL of the XQueue server
        :type url: str
        :param name: The name of the XQueue server
        :type name: str
        :param auth_basic: A tuple of (username, password)
        :type auth_basic: tuple
        :param auth_xqueue: A tuple of (username, password)
        :type auth_xqueue: tuple
        """
        self.url = url
        self.name = name
        self.auth_basic = auth_basic
        self.auth_xqueue = auth_xqueue
        self.session = None

    def __len__(self):
        """
        Returns the length of the XQueue
        """
        self._try_login()
        response = self._request(
            self.session.get,
            self._get_method_url('get_queuelen'),
            error_message=ERROR_LEN,
            params={
                'queue_name': self.name,
            },
        )
        try:
            length = int(response['content'])
        except (ValueError) as error:
            LOG.critical(ERROR_LEN, error)
            raise
        return length

    def __str__(self):
        return self.url

    def pop(self):
        """
        Get submission from the XQueue server

        :raises: ConnectionError, Timeout, ValueError, KeyError, Exception
        :returns: dict -- a single submission
        """
        self._try_login()
        response = self._request(
            self.session.get,
            self._get_method_url('get_submission'),
            error_message=ERROR_GET,
            params={
                'queue_name': self.name,
            },
        )
        LOG.debug(MESSAGE_GET_RESPONSE, response)
        return json.loads(response['content'])

    def put(self, xqueue_reply):
        """
        Post xqueue_reply to qserver for posting back to LMS

        :param xqueue_reply: The payload to be posted to the server
        :type xqueue_reply: dict
        :raises: ConnectionError, Timeout, Exception
        """
        self._try_login()
        response = self._request(
            self.session.post,
            self._get_method_url('put_result'),
            error_message=ERROR_POST_RESPONSE,
            data=xqueue_reply,
        )
        LOG.info(MESSAGE_RESPONSE, response)
        return response

    def _get_method_url(self, method):
        """
        Build an XQueue request URL

        :param method: The method to be called on the XQueue server
        :type method: str
        :returns: str -- the method's XQueue URL
        """
        return "{url_base}/xqueue/{method}/".format(
            url_base=self.url,
            method=method,
        )

    # TODO: should this return anything?
    def _try_login(self):
        """
        Login to the XQueue server

        :param auth_basic: A tuple of (username, password)
        :type auth_basic: tuple
        :param auth_xqueue: A tuple of (username, password)
        :type auth_xqueue: tuple
        :raises: ConnectionError, Timeout, Exception
        """
        if not self.session:
            self.session = requests.Session()
            self.session.auth = self.auth_basic
            self._request(
                self.session.post,
                self._get_method_url('login'),
                error_message=ERROR_CONNECT,
                data={
                    'username': self.auth_xqueue[0],
                    'password': self.auth_xqueue[1],
                },
            )

    def _request(self, method, url, error_message, **kwargs):
        """
        Make a request to the XQueue server

        :param method: The method to be executed by the server
        :type method: str
        :param url: The server URL
        :type url: str
        :param error_message: The message to be displayed on error
        :type error_message: str
        """
        try:
            request = method(url, **kwargs)
        except (ConnectionError, Timeout) as error:
            LOG.critical(error_message, error)
            raise
        try:
            # response = json.loads(request.text)
            response = request.json()
        except ValueError as error:
            LOG.critical(error_message, error)
            raise
        try:
            validate(response)
        except InvalidReturnCode as error:
            LOG.critical(error_message, error)
            raise
        return response
