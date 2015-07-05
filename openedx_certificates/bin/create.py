#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a standalone utility for generating certficiates.
It will use test data in tests/test_data.py for names and courses.
PDFs by default will be dropped in TMP_GEN_DIR for review

TODO: modes
- read from CSV: create many certs
- read from command line: create single cert
- write output to CSV and/or stdout
- optionally upload to S3

CHANGELOG:
- report output format is changed:
    - was: name, course, args.long_org, args.long_course, download_url,
    - now: course_id, name, grade, download_url
- logging format change: s/{hostname} /pid:/
- Doesn't upload to S3 by default
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import csv
import logging
import os
import random
import shutil
import sys

from gen_cert import CertificateGen
from openedx_certificates import settings
from tests.test_data import NAMES


logging.config.dictConfig(settings.get('LOGGING'))
LOG = logging.getLogger('certificates.create_pdfs')


def parse_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        '-c',
        '--course',
        help='optional course_id',
    )
    parser.add_argument(
        '-n',
        '--name',
        help='optional name for the cert',
    )
    parser.add_argument(
        '-g',
        '--grade',
        help='optional grading label to apply',
    )
    parser.add_argument(
        '-i',
        '--input',
        help='optional input CSV file to seed generation',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='file for generated output (TODO: default to stdout)',
    )
    parser.add_argument(
        '-u',
        '--upload',
        help='upload generated certs (default to S3)',
        default=False,
        action='store_true',
    )

    parser.add_argument(
        '-T',
        '--title-random',
        help='add random title after name',
        default=False,
        action='store_true',
    )
    args = parser.parse_args()
    args = vars(args)
    return args


def main(args):
    """
    Generates some pdfs using each template for different names for
    review in a pdf viewer.
    Will copy out the pdfs into the certs/ dir
    """
    LOG.debug('Launching %s', __name__)
    copy_dir = settings.get('TMP_GEN_DIR') + "+copy"
    certificate_data = []
    should_try_upload = args.get('upload')
    course = args.get('course')
    courses = settings.get('CERT_DATA').keys()
    grade = args.get('grade')
    name = args.get('name')
    names = NAMES
    path_input = args.get('input')

    if course:
        courses = [course]
    if name:
        names = [name]
    elif path_input:
        LOG.debug('Loading input file: %s', path_input)
        try:
            with open(path_input) as file_input:
                names = [
                    line.rstrip()
                    for line in file_input.readlines()
                ]
        except OSError:
            LOG.debug('No file: %s', path_input)
            pass
        LOG.debug('Loaded input file: %s: %s', path_input, names)

    try:
        os.makedirs(copy_dir)
        LOG.debug('Makedirs: %s', copy_dir)
    except OSError:
        pass

    for course in courses:
        for name in names:
            cert = CertificateGen(
                course,
                # TODO: we shouldn't pass AWS creds along
                aws_id=settings.get('CERT_AWS_ID'),
                aws_key=settings.get('CERT_AWS_KEY'),
            )
            title = None
            if args.get('title_random'):
                title = random.choice(stanford_cme_titles)[0]
            (download_uuid, verify_uuid, download_url) = cert.create_and_upload(
                name,
                upload=should_try_upload,
                copy_to_webroot=False,
                cleanup=False,
                designation=title,
                grade=grade,
            )
            certificate_data.append(
                (
                    course,
                    name,
                    grade,
                    download_url,
                )
            )
            directory_output = os.path.join(
                cert.dir_prefix,
                settings.get('S3_CERT_PATH'),
                download_uuid,
            )
            copy_dest = "{copy_dir}/{course}-{name}.pdf".format(
                copy_dir=copy_dir,
                name=name.replace(' ', '-').replace('/', '-'),
                course=course.replace('/', '-')
            )

            if _try_copy_file(
                directory_output,
                copy_dest,
                name,
                download_uuid,
                verify_uuid,
                download_uuid,
            ):
                LOG.info("Created %s", copy_dest)
            else:
                LOG.error("Unable to copy file: %s", copy_dest)
    _write_output(certificate_data, args.get('input'))
    LOG.debug('Closing %s', __name__)


def _try_copy_file(
    directory_output,
    copy_dest,
    name,
    download_uuid,
    verify_uuid,
    download_uuid,
):
    try:
        shutil.copyfile(
            "{0}/{1}".format(
                directory_output,
                settings.get('CERT_FILENAME'),
            ),
            unicode(copy_dest.decode('utf-8'))
        )
    except Exception as error:
        LOG.error(
            "{error}: {name}: {download_uuid}: {verify_uuid}: {download_uuid}: {directory_output}: {copy_dest}",
            {
                'error': error,
                'name': name,
                'download_uuid': download_uuid,
                'verify_uuid': verify_uuid,
                'download_uuid': download_uuid,
                'directory_output': directory_output,
                'copy_dest': copy_dest,
            },
        )
        raise
    return True


def _write_output(certificate_data, input_file=None):
    if input_file:
        LOG.debug('Write output to file: %s: %s', input_file, certificate_data)
        try:
            with open(input_file, 'wb') as file_report:
                _write(certificate_data, file_report)
            LOG.debug('Wrote output to file')
        except IOError as error:
            LOG.error("Unable to open report file: %s", error)
    else:
        LOG.debug('Write output to stdout: %s: %s', input_file, certificate_data)
        _write(certificate_data, sys.stdout)
        LOG.debug('Wrote output to file')

def _write(rows, file_output):
    csv_writer = csv.writer(file_output, quoting=csv.QUOTE_ALL)
    csv_writer.writerows(rows)


if __name__ == '__main__':
    LOG = logging.getLogger('openedx_certificates.bin.create')
    args = parse_args()
    main(args)
