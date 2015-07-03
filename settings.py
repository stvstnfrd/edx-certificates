# -*- coding: utf-8 -*-

"""
Settings file for the certificate agent
"""

import json
import os
import yaml

from logsettings import get_logger_config
from path import path

import openedx_certificates

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH
ENV_ROOT = REPO_PATH.dirname()

# Override CERT_PRIVATE_DIR if you have have private templates, fonts, etc.
CERT_PRIVATE_DIR = REPO_PATH

# If CERT_PRIVATE_DIR is set in the environment use it

if 'CERT_PRIVATE_DIR' in os.environ:
    CERT_PRIVATE_DIR = path(os.environ['CERT_PRIVATE_DIR'])

# This needs to be set on MacOS or anywhere you want logging to simply go
# to an output file.
LOGGING_DEV_ENV = openedx_certificates.settings.get('LOGGING_DEV_ENV')
LOGGING = get_logger_config(ENV_ROOT,
                            logging_env="dev",
                            local_loglevel="INFO",
                            dev_env=LOGGING_DEV_ENV,
                            debug=False)

# Default for the gpg dir
CERT_GPG_DIR = '{0}/.gnupg'.format(os.environ['HOME'])
# dummy key:
# https://raw.githubusercontent.com/edx/configuration/master/playbooks/roles/certs/files/example-private-key.txt

# load settings from env.json and auth.json
if os.path.isfile(ENV_ROOT / "env.json"):
    with open(ENV_ROOT / "env.json") as env_file:
        ENV_TOKENS = json.load(env_file)
    CERT_GPG_DIR = ENV_TOKENS.get('CERT_GPG_DIR', CERT_GPG_DIR)
    local_loglevel = ENV_TOKENS.get('LOCAL_LOGLEVEL', 'INFO')
    LOGGING = get_logger_config(openedx_certificates.settings.get('LOG_DIR'),
                                logging_env=ENV_TOKENS.get('LOGGING_ENV', 'dev'),
                                local_loglevel=local_loglevel,
                                debug=False,
                                dev_env=LOGGING_DEV_ENV,
                                service_variant=os.environ.get('SERVICE_VARIANT', None))
    CERT_PRIVATE_DIR = ENV_TOKENS.get('CERT_PRIVATE_DIR', CERT_PRIVATE_DIR)

CERT_BUCKET = openedx_certificates.settings.get('CERT_BUCKET')
# This is the base URL that will be displayed to the user in the dashboard
CERT_DOWNLOAD_URL = openedx_certificates.settings.get('CERT_DOWNLOAD_URL') or 'https://{}.s3.amazonaws.com'.format(CERT_BUCKET)
CERT_VERIFY_URL = openedx_certificates.settings.get('CERT_VERIFY_URL') or 'http://{}.s3.amazonaws.com'.format(CERT_BUCKET)

# Use the custom CERT_PRIVATE_DIR for paths to the
# template sub directory and the cert data config

TEMPLATE_DIR = os.path.join(
    CERT_PRIVATE_DIR,
    openedx_certificates.settings.get('TEMPLATE_DATA_SUBDIR'),
)

CERT_DATA_FILE = openedx_certificates.settings.get('CERT_DATA_FILE')
with open(os.path.join(CERT_PRIVATE_DIR, CERT_DATA_FILE)) as f:
    CERT_DATA = yaml.load(f.read().decode("utf-8"))

# Locale and Translations
DEFAULT_LOCALE = 'en_US'
DEFAULT_TRANSLATIONS = {
    'en_US': {
        'success_text': u'has successfully completed a free online offering of',
        'grade_interstitial': u"with {grade}.",
        'disclaimer_text': openedx_certificates.settings.get('CERTS_SITE_DISCLAIMER_TEXT'),
        'verify_text': u"Authenticity can be verified at {verify_link}",
    },
}
