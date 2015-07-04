# -*- coding: utf-8 -*-
"""
Load settings from JSON
"""

import json
import os
import os.path
import yaml


from logsettings import get_logger_config


def _load_json(filepath, filename):
    path_json = os.path.join(filepath, filename)
    try:
        with open(path_json) as file_json:
            result = json.load(file_json)
    except IOError:
        result = {}
    return result

def _load_environ(prefix='CERT_'):
    environ = {}
    for key in os.environ:
        if key.startswith(prefix):
            environ[key] = os.environ[key]
    return environ


_path_file = os.path.abspath(__file__)
_path_module = os.path.dirname(_path_file)
_path_package = os.path.dirname(_path_module)
_path_application = os.path.dirname(_path_package)

_auth = _load_json(_path_application, 'auth.json')
_env = _load_json(_path_application, 'env.json')
_default = _load_json(_path_module, 'config.json')
_environ = _load_environ()
_custom = {}


def get(key, default=None, course_id=None):
    def _get(key, default=None):
        for config in [_environ, _custom, _auth, _env, _default]:
            if key in config:
                return config[key]
        return default
    if course_id:
        if course_id in _get('CERT_DATA'):
            if key in _get('CERT_DATA')[course_id]:
                return _get('CERT_DATA')[course_id][key]
    return _get(key, default)

def update(key, value):
    _custom[key] = value
    return value


if get('CERT_BUCKET'):
    if not get('CERT_VERIFY_URL'):
        update(
            'CERT_VERIFY_URL',
            "http://{}.s3.amazonaws.com".format(get('CERT_BUCKET'))
        )
    if not get('CERT_DOWNLOAD_URL'):
        update(
            'CERT_DOWNLOAD_URL',
            "https://{}.s3.amazonaws.com".format(get('_CERT_BUCKET'))
        )

if not get('CERT_GPG_DIR'):
    update(
        'CERT_GPG_DIR',
        "{0}/.gnupg".format(
            os.environ['HOME'],
        )
    )

if get('CERT_PRIVATE_DIR') and get('TEMPLATE_DATA_SUBDIR'):
    update(
        u'TEMPLATE_DIR',
        os.path.join(
            get('CERT_PRIVATE_DIR'),
            get('TEMPLATE_DATA_SUBDIR'),
        )
    )

if get('CERT_DATA_FILE'):
    update(
        'CERT_DATA_FILE',
        os.path.join(
            get('CERT_PRIVATE_DIR'),
            get('CERT_DATA_FILE'),
        )
    )
    try:
        with open(get('CERT_DATA_FILE')) as file_cert_data:
            _cert_data = yaml.load(file_cert_data.read().decode('utf-8'))
    except IOError:
        _cert_data = {}
    update('CERT_DATA', _cert_data)

DEFAULT_TRANSLATIONS = {
    'en_US': {
        'success_text': u'has successfully completed a free online offering of',
        'grade_interstitial': u"with {grade}.",
        'disclaimer_text': get('CERTS_SITE_DISCLAIMER_TEXT'),
        'verify_text': u"Authenticity can be verified at {verify_link}",
    },
}

LOGGING = get_logger_config(
    get('LOG_DIR', _path_application),
    logging_env=get('LOGGING_ENV'),
    local_loglevel=get('LOCAL_LOGLEVEL'),
    debug=get('DEBUG'),
    dev_env=get('LOGGING_DEV_ENV'),
)
