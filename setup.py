"""
TODO
"""
from os import getcwd
from os import path
from setuptools import setup


version = '0.1.0'
description = __doc__.strip().split('\n')[0]
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as file_in:
    long_description = file_in.read()


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)

print('FUNK', getcwd())

setup(
    name='openedx-certifcates',
    version=version,
    description=description,
    long_description=long_description,
    author='stv',
    author_email='stv@stanford.edu',
    url='https://github.com/Stanford-Online/openedx-certificates',
    license='AGPL-3.0',
    packages=[
        'openedx_certificates',
    ],
    install_requires=[
        'argparse==1.2.1',
        'boto==2.27.0',
        'ddt',
        'edx-opaque-keys==0.4.0',
        'gnupg==1.4.0',
        'nose==1.2.1',
        'path.py==2.4.1',
        'pep8==1.5.7',
        'Pillow<6.0.0',
        'pyPdf2==1.23',
        'python-bidi==0.3.4',
        'PyYAML==3.11',
        'reportlab==3.1.44',
        'requests==2.3.0',
        'babel==1.3',
        # mock
        # six
    ],
    package_dir={
        'openedx_certificates': 'openedx_certificates',
    },
    package_data={
        '': [
            '*.txt',
        ],
        "openedx_certificates": [
            '*',
        ],
    },
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='openedx_certificates.tests',
    tests_require=[
        'coverage',
        'coveralls',
        'mock',
        'pep8',
        'tox',
    ],
)
