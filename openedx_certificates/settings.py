# -*- coding: utf-8 -*-
"""
Load settings from JSON
"""

import json
import os
import os.path
import yaml

from path import path

from logsettings import get_logger_config

_ROOT_PATH = os.path.abspath(__file__)
_ROOT_PATH = os.path.dirname(_ROOT_PATH)
_REPO_PATH = _ROOT_PATH
_ENV_ROOT = os.path.dirname(os.path.dirname(_REPO_PATH))


def _load_jsons(filename):
    path_json_auth_default = os.path.join(_REPO_PATH, filename)
    path_json_auth_custom = os.path.join(_ENV_ROOT, filename)
    json_auth_custom = _load_json(path_json_auth_custom)
    json_auth_default = _load_json(path_json_auth_default)
    json_auth_merged = json_auth_default.copy()
    json_auth_merged.update(json_auth_custom)
    return json_auth_merged


def _load_json(path_json):
    try:
        with open(path_json) as file_json:
            result = json.load(file_json)
    except IOError:
        result = {}
    return result

_AUTH = _load_jsons('auth.json')
_ENV = _load_jsons('env.json')

# Override _CERT_PRIVATE_DIR if you have have private templates, fonts, etc.
_CERT_PRIVATE_DIR = _REPO_PATH
if 'CERT_PRIVATE_DIR' in os.environ:
    _CERT_PRIVATE_DIR = path(os.environ['CERT_PRIVATE_DIR'])
else:
    _CERT_PRIVATE_DIR = _ENV.get('CERT_PRIVATE_DIR')


# TODO: add to default auth.json file for backward compat
# else: delete
_AUTH['QUEUE_USER'] = _AUTH.get('QUEUE_USER', 'lms')
_CERT_BUCKET = _ENV.get('CERT_BUCKET')
_ENV['CERT_VERIFY_URL'] = _ENV.get(
    'CERT_VERIFY_URL',
    'http://{}.s3.amazonaws.com'.format(_CERT_BUCKET)
)
_ENV['CERT_DOWNLOAD_URL'] = _ENV.get(
    'CERT_DOWNLOAD_URL',
    'https://{}.s3.amazonaws.com'.format(_CERT_BUCKET)
)
_ENV['CERT_GPG_DIR'] = _ENV.get(
    'CERT_GPG_DIR',
    "{0}/.gnupg".format(
        os.environ['HOME'],
    )
)
_ENV[u'TEMPLATE_DIR'] = os.path.join(
    _CERT_PRIVATE_DIR,
    _ENV.get('TEMPLATE_DATA_SUBDIR'),
)

LOGGING = get_logger_config(
    _ENV.get('LOG_DIR', _ENV_ROOT),
    logging_env=_ENV.get('LOGGING_ENV'),
    local_loglevel=_ENV.get('LOCAL_LOGLEVEL'),
    debug=_ENV.get('DEBUG'),
    dev_env=_ENV.get('LOGGING_DEV_ENV'),
)

def get(key, default=None):
    return _AUTH.get(key, _ENV.get(key, default))

# Specify these credentials before running the test suite
# or ensure that your .boto file has write permission
# to the bucket.
# CERT_AWS_KEY = AUTH_TOKENS.get('CERT_AWS_KEY')
# CERT_AWS_ID = AUTH_TOKENS.get('CERT_AWS_ID')

from pprint import pprint
pprint(_AUTH)
pprint(_ENV)

_CERT_DATA_FILE = _ENV.get('CERT_DATA_FILE')
_CERT_DATA_FILE = os.path.join(
    _CERT_PRIVATE_DIR,
    _CERT_DATA_FILE
)
try:
    with open(_CERT_DATA_FILE) as file_cert_data:
        _CERT_DATA = yaml.load(file_cert_data.read().decode("utf-8"))
except IOError:
    _CERT_DATA = {}
_ENV['CERT_DATA'] = _CERT_DATA

# Locale and Translations

DEFAULT_TRANSLATIONS = {
    'en_US': {
        'success_text': u'has successfully completed a free online offering of',
        'grade_interstitial': u"with {grade}.",
        'disclaimer_text': _ENV.get('CERTS_SITE_DISCLAIMER_TEXT'),
        'verify_text': u"Authenticity can be verified at {verify_link}",
    },
}


# This AMI might work for people that _just_ want to quickly deploy and
# test out a _vanilla_ server, but I would recommend _against_ doing _any_
# development of customization with this AMI.
