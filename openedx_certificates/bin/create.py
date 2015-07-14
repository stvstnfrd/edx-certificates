#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a standalone utility for generating certficiates.
It will use test data in tests/test_data.py for names and courses.
PDFs by default will be dropped in TMP_GEN_DIR for review

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
import logging.config
import os
import random
import shutil
import sys

# from gen_cert import CertificateGen
from openedx_certificates import settings
from openedx_certificates import exceptions


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
        action='append',
        dest='courses',
    )
    parser.add_argument(
        '-n',
        '--name',
        help='optional names for the cert',
        action='append',
        dest='names',
    )
    parser.add_argument(
        '-g',
        '--grade',
        help='optional grading label to apply',
        # default='Pass',
    )

    parser.add_argument(
        '-t',
        '--title',
        help='add title after name',
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
    certificate_data = []
    courses = args.get('courses') or settings.get('CERT_DATA').keys()
    grade = args.get('grade')
    names = args.get('names', [])
    title = args.get('title')
    if title:
        title = (title, title)  # form of ('PhD', 'PhD')
    _process_all_certs(courses, names, grade, title)
    LOG.debug('Closing %s', __name__)


def _process_all_certs(courses, names, grade, title):
    copy_dir = settings.get('TMP_GEN_DIR') + "+copy"
    try:
        os.makedirs(copy_dir)
        LOG.debug('Makedirs: %s', copy_dir)
    except OSError:
        pass
    csv_writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    for course in courses:
        for name in names:
            print(course, name, grade, title)
            continue
            row = _process_single_cert(course, name, grade, title)
            csv_writer.writerow(row)

def _process_single_cert(course, name, grade, title, copy_dir):
    cert = CertificateGen(
        course,
        # TODO: we shouldn't pass AWS creds along
        aws_id=settings.get('CERT_AWS_ID'),
        aws_key=settings.get('CERT_AWS_KEY'),
    )
    (download_uuid, verify_uuid, download_url) = cert.create_and_upload(
        name,
        upload=settings.get('S3_UPLOAD'),
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
    copy_dest = _try_copy_file(
        directory_output,
        name,
        course,
        download_uuid,
        verify_uuid,
        copy_dir,
    )
    if copy_dest:
        LOG.info("Created %s", copy_dest)

def _try_copy_file(
    directory_output,
    copy_dest,
    name,
    course,
    download_uuid,
    verify_uuid,
    copy_dir,
):
    copy_dest = "{copy_dir}/{course}-{name}.pdf".format(
        copy_dir=copy_dir,
        name=name.replace(' ', '-').replace('/', '-'),
        course=course.replace('/', '-')
    )
    try:
        shutil.copyfile(
            "{0}/{1}".format(
                directory_output,
                settings.get('CERT_FILENAME'),
            ),
            unicode(copy_dest.decode('utf-8'))
        )
    except Exception as error:
        body = {
            'username': name,
            'course_id': course,
        }
        message = exceptions.prettify(error, body=body)
        LOG.error('%s', error)
        return None
    return copy_dest


if __name__ == '__main__':
    LOG = logging.getLogger('openedx_certificates.bin.create')
    args = parse_args()
    main(args)
