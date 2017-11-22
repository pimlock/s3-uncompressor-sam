import json
import logging
import os

import boto3 as boto3

from s3_uncompressor.util.log import setup_lambda_logging
from s3_uncompressor.util.s3 import S3ObjectInfo, S3ZipUncompressor

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, context, s3_client, dest_bucket=None):
        """
        :param context: context of the Lambda function
        :param s3_client: S3 client that will be used to read/write from S3 bucket
        :param dest_bucket: destination bucket where files will be uncompressed (if not provided, the contents will be uncompressed to the same bucket)
        """
        self.context = context
        self.dest_bucket = dest_bucket

        self.uncompressors = [
            S3ZipUncompressor(s3_client)
        ]

    def handle(self, event):
        """
        :param dict event: input of the Lambda function (dict)
        """
        records = event.get('Records', [])

        for record in records:
            if not self._is_valid_s3_notification_record(record):
                logger.warning('Invalid record, skipping: %s', json.dumps(record, indent=2))
                continue

            self._try_uncompress(record)

    def _try_uncompress(self, record):
        s3_object_info = self._create_s3_object_info(record)

        uncompressor = self._find_uncompressor(s3_object_info)
        if not uncompressor:
            logger.debug('Skipping object "%s", not an archive or we don\'t support it.', s3_object_info)
            return

        uncompressor.uncompress(s3_object_info, self.dest_bucket)

    def _find_uncompressor(self, s3_object_info):
        for uncompressor in self.uncompressors:
            if uncompressor.can_uncompress(s3_object_info):
                return uncompressor

        return None

    def _create_s3_object_info(self, record):
        s3_info = record['s3']
        object_info = s3_info['object']

        return S3ObjectInfo(
            s3_info['bucket']['name'],
            object_info['key'],
            object_info['size']
        )

    def _is_valid_s3_notification_record(self, record):
        if record.get('eventName') != 'ObjectCreated:Put':
            return False

        if record.get('s3') is None:
            return False

        s3_info = record['s3']
        if s3_info.get('bucket') is None:
            return False

        if s3_info.get('object') is None:
            return False

        return True


def main(event, context):
    setup_lambda_logging()

    s3_client = boto3.client('s3')

    handler = Handler(context, s3_client, get_destination_bucket())
    handler.handle(event)


def get_destination_bucket():
    destination_bucket = os.environ.get('DESTINATION_BUCKET')
    logger.info('Environment variable DESTINATION_BUCKET="%s"', destination_bucket)
    if not destination_bucket:
        destination_bucket = None

    return destination_bucket
