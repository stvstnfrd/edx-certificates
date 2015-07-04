#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a standalone utility for generating certficiates.
It will use test data in tests/test_data.py for names and courses.
PDFs by default will be dropped in TMP_GEN_DIR for review

TODO: read from CSV
`course_id,name,grade`
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

stanford_cme_titles = (
    ('AuD', 'AuD'),
    ('DDS', 'DDS'),
    ('DO', 'DO'),
    ('MD', 'MD'),
    ('MD,PhD', 'MD,PhD'),
    ('MBBS', 'MBBS'),
    ('NP', 'NP'),
    ('PA', 'PA'),
    ('PharmD', 'PharmD'),
    ('PhD', 'PhD'),
    ('RN', 'RN'),
    ('Other', 'Other'),
    ('None', 'None'),
    (None, None),
)


def parse_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        '-c',
        '--course-id',
        help='optional course_id',
    )
    parser.add_argument(
        '-n',
        '--name',
        help='optional name for the cert',
    )
    parser.add_argument(
        '-t',
        '--template-file',
        help='optional template file',
    )
    parser.add_argument(
        '-o',
        '--long-org',
        help='optional long org',
        default='',
    )
    parser.add_argument(
        '-l',
        '--long-course',
        help='optional long course',
        default='',
    )
    parser.add_argument(
        '-i',
        '--issued-date',
        help='optional issue date',
    )
    parser.add_argument(
        '-T',
        '--assign-title',
        help='add random title after name',
        default=False,
        action='store_true',
    )
    parser.add_argument(
        '-f',
        '--input-file',
        help='optional input file for names, one name per line',
    )
    parser.add_argument(
        '-r',
        '--report-file',
        help='optional report file for generated output',
    )
    parser.add_argument(
        '-R',
        '--no-report',
        help='Do not comment on generated output',
        default=False,
        action='store_true',
    )
    parser.add_argument(
        '-G',
        '--grade-text',
        help='optional grading label to apply',
    )
    parser.add_argument(
        '-U',
        '--no-upload',
        help='skip s3 upload step',
        default=False,
        action='store_true',
    )
    return parser.parse_args()


def main(args):
    """
    Generates some pdfs using each template
    for different names for review in a pdf
    viewer.
    Will copy out the pdfs into the certs/ dir
    """
    pdf_dir = settings.get('TMP_GEN_DIR')
    copy_dir = pdf_dir + "+copy"
    certificate_data = []
    upload_files = not args.no_upload
    course_list = settings.get('CERT_DATA').keys()
    grade = None
    should_write_report_to_stdout = not args.no_report

    if args.grade_text:
        grade = args.grade_text
    if args.course_id:
        course_list = [args.course_id]
    if args.name:
        name_list = [args.name]
    elif args.input_file:
        try:
            with open(args.input_file) as file_input:
                name_list = [line.rstrip() for line in file_input.readlines()]
        except OSError:
            name_list = NAMES
    else:
        name_list = NAMES

    for directory_output in [pdf_dir, copy_dir]:
        try:
            shutil.rmtree(directory_output)
        except OSError:
            pass
    try:
        os.makedirs(copy_dir)
    except OSError:
        pass

    for course in course_list:
        for name in name_list:
            cert = CertificateGen(
                course,
                args.template_file,
                aws_id=settings.get('CERT_AWS_ID'),
                aws_key=settings.get('CERT_AWS_KEY'),
                dir_prefix=pdf_dir,
                long_org=args.long_org,
                long_course=args.long_course,
                issued_date=args.issued_date,
            )
            title = None
            if args.assign_title:
                title = random.choice(stanford_cme_titles)[0]
            (download_uuid, verify_uuid, download_url) = cert.create_and_upload(
                name,
                upload=upload_files,
                copy_to_webroot=False,
                cleanup=False,
                designation=title,
                grade=grade,
            )
            certificate_data.append(
                (
                    name,
                    course,
                    args.long_org,
                    args.long_course,
                    download_url,
                )
            )
            gen_dir = os.path.join(
                cert.dir_prefix,
                settings.get('S3_CERT_PATH'),
                download_uuid,
            )
            copy_dest = "{copy_dir}/{course}-{name}.pdf".format(
                copy_dir=copy_dir,
                name=name.replace(' ', '-').replace('/', '-'),
                course=course.replace('/', '-')
            )

            try:
                shutil.copyfile(
                    "{0}/{1}".format(
                        gen_dir,
                        settings.get('CERT_FILENAME'),
                    ),
                    unicode(copy_dest.decode('utf-8'))
                )
            except Exception as error:
                LOG.error(
                    "{error}: {name}: {download_uuid}: {verify_uuid}: {download_uuid}: {gen_dir}: {copy_dest}",
                    {
                        'error': error,
                        'name': name,
                        'download_uuid': download_uuid,
                        'verify_uuid': verify_uuid,
                        'download_uuid': download_uuid,
                        'gen_dir': gen_dir,
                        'copy_dest': copy_dest,
                    },
                )
                raise
            LOG.info("Created %s", copy_dest)

    if args.report_file:
        try:
            with open(args.report_file, 'wb') as file_report:
                csv_writer = csv.writer(file_report, quoting=csv.QUOTE_ALL)
                csv_writer.writerows(certificate_data)
            should_write_report_to_stdout = False
        except IOError as error:
            LOG.error("Unable to open report file: %s", error)
    if should_write_report_to_stdout:
        for row in certificate_data:
            print '\t'.join(row)
            LOG.DEBUG(': '.join(row))

if __name__ == '__main__':
    args = parse_args()
    main(args)
