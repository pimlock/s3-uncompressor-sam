import logging
import os
import zipfile
from abc import abstractmethod
from io import BytesIO

logger = logging.getLogger(__name__)


class S3ObjectInfo:
    def __init__(self, bucket_name, object_key, object_size=None):
        self._bucket_name = bucket_name
        self._object_key = object_key

        self._object_size = object_size

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def object_key(self):
        return self._object_key

    @property
    def object_size(self):
        return self._object_size

    def __str__(self):
        return '{}/{}'.format(self._bucket_name, self._object_key)


class S3Uncompressor:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    @abstractmethod
    def uncompress(self, s3_object_info, dest_bucket=None):
        """
        :type s3_object_info: s3.S3ObjectInfo
        :type dest_bucket: str
        :return: NoneType
        """
        raise NotImplementedError()

    @abstractmethod
    def can_uncompress(self, s3_object_info):
        """
        :type s3_object_info: s3.S3ObjectInfo
        :return: boolean
        """
        raise NotImplementedError()

    def _download_s3_file(self, s3_object_info):
        zip_data = BytesIO()
        self.s3_client.download_fileobj(s3_object_info.bucket_name, s3_object_info.object_key, zip_data)

        return zip_data


class S3ZipUncompressor(S3Uncompressor):
    def __init__(self, s3_client):
        super().__init__(s3_client)

    def uncompress(self, s3_object_info, dest_bucket=None):
        """
        :type s3_object_info: s3.S3ObjectInfo
        :type dest_bucket: str
        """
        if not dest_bucket:
            dest_bucket = s3_object_info.bucket_name

        logger.info('Uncompressing S3 object: "%s" to destination bucket: "%s"', s3_object_info, dest_bucket)

        s3_filename = os.path.basename(s3_object_info.object_key)
        s3_dirname = os.path.dirname(s3_object_info.object_key)

        key_prefix = ''
        if s3_dirname:
            key_prefix = s3_dirname + '/'

        zip_file = zipfile.ZipFile(self._download_s3_file(s3_object_info))
        for name in zip_file.namelist():
            data = zip_file.read(name)

            self.s3_client.put_object(
                Body=data,
                Bucket=dest_bucket,
                Key=key_prefix + s3_filename[:-4] + '/' + name
            )

    def can_uncompress(self, s3_object_info):
        """
        :type s3_object_info: s3.S3ObjectInfo
        :return: boolean
        """
        return s3_object_info.object_key.endswith('.zip')
