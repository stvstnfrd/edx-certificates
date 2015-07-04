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


_path_file = os.path.abspath(__file__)
_path_module = os.path.dirname(_path_file)
_path_package = os.path.dirname(_path_module)
_path_application = os.path.dirname(_path_package)

_auth = _load_json(_path_application, 'auth.json')
_env = _load_json(_path_application, 'env.json')
_default = _load_json(_path_module, 'config.json')
_custom = {}


def get(key, default=None, course_id=None):
    # TODO: it may be more performant to merge the dicts together once
    def _get(key, default=None):
        for config in [_custom, _auth, _env, _default]:
            if key in config:
                return config[key]
        return default
    if course_id:
        if course_id in _get('CERT_DATA'):
            if key in _get('CERT_DATA')[course_id]:
                return _get('CERT_DATA')[course_id][key]
    return _get(key, default)

# TODO: rename
def set(key, value):
    _custom[key] = value
    return value


_CERT_BUCKET = get('CERT_BUCKET')
if _CERT_BUCKET:
    if not get('CERT_VERIFY_URL'):
        set(
            'CERT_VERIFY_URL',
            "http://{}.s3.amazonaws.com".format(_CERT_BUCKET)
        )
    if not get('CERT_DOWNLOAD_URL'):
        set(
            'CERT_DOWNLOAD_URL',
            "https://{}.s3.amazonaws.com".format(_CERT_BUCKET)
        )

if not get('CERT_GPG_DIR'):
    set(
        'CERT_GPG_DIR',
        "{0}/.gnupg".format(
            os.environ['HOME'],
        )
    )

# Override _CERT_PRIVATE_DIR if you have have private templates, fonts, etc.
if 'CERT_PRIVATE_DIR' in os.environ:
    set('CERT_PRIVATE_DIR', path(os.environ['CERT_PRIVATE_DIR']))

if get('CERT_PRIVATE_DIR') and get('TEMPLATE_DATA_SUBDIR'):
    set(
        u'TEMPLATE_DIR',
        os.path.join(
            get('CERT_PRIVATE_DIR'),
            get('TEMPLATE_DATA_SUBDIR'),
        )
    )

if get('CERT_DATA_FILE'):
    set(
        'CERT_DATA_FILE',
        os.path.join(
            get('CERT_PRIVATE_DIR'),
            get('CERT_DATA_FILE'),
        )
    )
    try:
        with open(get('CERT_DATA_FILE')) as file_cert_data:
            _CERT_DATA = yaml.load(file_cert_data.read().decode('utf-8'))
    except IOError:
        _CERT_DATA = {}
    set('CERT_DATA', _CERT_DATA)

# Locale and Translations
DEFAULT_TRANSLATIONS = {
    'en_US': {
        'success_text': u'has successfully completed a free online offering of',
        'grade_interstitial': u"with {grade}.",
        'disclaimer_text': get('CERTS_SITE_DISCLAIMER_TEXT'),
        'verify_text': u"Authenticity can be verified at {verify_link}",
    },
}

# Default for the gpg dir
# dummy key:
# https://raw.githubusercontent.com/edx/configuration/master/playbooks/roles/certs/files/example-private-key.txt

LOGGING = get_logger_config(
    get('LOG_DIR', _path_application),
    logging_env=get('LOGGING_ENV'),
    local_loglevel=get('LOCAL_LOGLEVEL'),
    debug=get('DEBUG'),
    dev_env=get('LOGGING_DEV_ENV'),
)


# TODO: add all `CERT_*` envvars to dict
pprint(_auth)
pprint(_env)
pprint(_default)
pprint(_custom)
print(get('DEBUG'))
print(get('VERSION'))
print(get('VERSION', course_id='Medicine/Sci-Write/Fall2014'))
