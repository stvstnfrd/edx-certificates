# -*- coding: utf-8 -*-
"""
Load settings from JSON
"""

import json
import os.path

ROOT_PATH = os.path.abspath(__file__)
ROOT_PATH = os.path.dirname(ROOT_PATH)
REPO_PATH = ROOT_PATH
ENV_ROOT = os.path.dirname(os.path.dirname(REPO_PATH))

def _load_jsons(filename):
    path_json_auth_default = os.path.join(REPO_PATH, filename)
    path_json_auth_custom = os.path.join(ENV_ROOT, filename)
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

AUTH = _load_jsons('auth.json')
ENV = _load_jsons('env.json')




# TODO: add to default auth.json file for backward compat
# else: delete
AUTH['QUEUE_USER'] = AUTH.get('QUEUE_USER', 'lms')

def get(key, default=None):
    return AUTH.get(key, ENV.get(key, default))

# Specify these credentials before running the test suite
# or ensure that your .boto file has write permission
# to the bucket.
# CERT_AWS_KEY = AUTH_TOKENS.get('CERT_AWS_KEY')
# CERT_AWS_ID = AUTH_TOKENS.get('CERT_AWS_ID')

print(AUTH)
print(ENV)
print(get('QUEUE_PASS'))
print(get('DEBUG'))


# This AMI might work for people that _just_ want to quickly deploy and
# test out a _vanilla_ server, but I would recommend _against_ doing _any_
# development of customization with this AMI.
