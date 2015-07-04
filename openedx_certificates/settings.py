# -*- coding: utf-8 -*-
"""
Load settings from JSON

application-wide
-> env.json

instance-wide
-> auth.json

env vars?

course-wide
-> cert-data.yml

user-wide
-> ??? from LMS ???

request-wide
-> XQueue
"""

import json
import os
import os.path
from pprint import pprint
import yaml

from path import path

from logsettings import get_logger_config


def _load_json(filepath, filename):
    path_json = os.path.join(filepath, filename)
    try:
        with open(path_json) as file_json:
            result = json.load(file_json)
    except IOError:
        result = {}
    return result


_ROOT_PATH = os.path.abspath(__file__)
_ROOT_PATH = os.path.dirname(_ROOT_PATH)
_REPO_PATH = _ROOT_PATH
_ENV_ROOT = os.path.dirname(os.path.dirname(_REPO_PATH))
_AUTH = _load_json(_ENV_ROOT, 'auth.json')
_ENV = _load_json(_ENV_ROOT, 'env.json')
_default = _load_json(_REPO_PATH, 'config.json')

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
    _ENV.get('TEMPLATE_DATA_SUBDIR') or '',
)

LOGGING = get_logger_config(
    _ENV.get('LOG_DIR', _ENV_ROOT),
    logging_env=_ENV.get('LOGGING_ENV'),
    local_loglevel=_ENV.get('LOCAL_LOGLEVEL'),
    debug=_ENV.get('DEBUG'),
    dev_env=_ENV.get('LOGGING_DEV_ENV'),
)

# Specify these credentials before running the test suite
# or ensure that your .boto file has write permission
# to the bucket.
# CERT_AWS_KEY = AUTH_TOKENS.get('CERT_AWS_KEY')
# CERT_AWS_ID = AUTH_TOKENS.get('CERT_AWS_ID')

pprint(_AUTH)
pprint(_ENV)
pprint(_default)

_CERT_DATA_FILE = _ENV.get('CERT_DATA_FILE')
_CERT_DATA_FILE = os.path.join(
    _CERT_PRIVATE_DIR,
    _CERT_DATA_FILE or ''
)
try:
    with open(_CERT_DATA_FILE) as file_cert_data:
        _CERT_DATA = yaml.load(file_cert_data.read().decode('utf-8'))
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

# Default for the gpg dir
# dummy key:
# https://raw.githubusercontent.com/edx/configuration/master/playbooks/roles/certs/files/example-private-key.txt


def get(key, default=None):
    # TODO: it may be more performant to merge the dicts together once
    for config in [_AUTH, _ENV, _default]:
        if key in config:
            return config[key]
    return default

# TODO: add all `CERT_*` envvars to dict
print(get('DEBUG'))
