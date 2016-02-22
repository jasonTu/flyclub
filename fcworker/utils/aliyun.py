#!/bin/env python
# coding: utf-8

import os
import logging
from httplib import HTTPException

from oss.oss_api import OssAPI
from oss.oss_util import delete_all_objects

from common.constants import VENDOR_TYPE_ALIOSS
from utils.exceptions import (
    VendorConnectionError, ResourceIOError, ResourceMissing
)


class AliyunStorage(object):

    """Aliyun OSS access interface."""

    __vendor_type__ = VENDOR_TYPE_ALIOSS

    def __init__(self, **kwargs):
        """Init OSS API."""
        self.id = kwargs.get('id')
        self.oss_url = kwargs.get('url')
        self.priority = kwargs.get('priority', 0)
        self.oss_bucket = kwargs.get('bucket')
        self.access_key = kwargs.get('access_key')
        self.access_secret = kwargs.get('access_secret')
        self.oss = OssAPI(self.oss_url, self.access_key, self.access_secret)

    @classmethod
    def getStorageInfo(cls):
        """Generic storage information."""
        return {
            'vendor': cls.__vendor_type__,
        }

    def writeFile(self, srcPath, srcFile, dstPrefix, dstFile, overwrite=True):
        """Upload file to OSS with prefix dstPath."""
        mime_type = 'application/octet-stream'
        srcFilePath = os.path.join(srcPath, srcFile)
        dstFilePath = os.path.join(dstPrefix, dstFile)
        print 'WRITE srcFilePath:%s' % srcFilePath
        print 'WRITE dstFilePath:%s' % dstFilePath
        try:
            res = self.oss.put_object_from_file(
                self.oss_bucket,
                dstFilePath,
                srcFilePath,
                content_type=mime_type
            )
            print 'WRITE %s\n%s' % (res.status, res.read())
            if res.status != 200:
                logging.error('Fail to save file [%s] to OSS: %s\n%s',
                              srcPath, res.status, res.read())
                raise ResourceIOError('Fail to save file [%s] to OSS [%s]' % (
                    srcFilePath, dstFilePath))
        except HTTPException:
            logging.error('Fail to save file [%s] to OSS [%s]',
                          srcFilePath, dstFilePath, exc_info=True)
            raise VendorConnectionError
        except IOError:
            logging.error('Fail to save file [%s] to OSS [%s]',
                          srcFilePath, dstFilePath, exc_info=True)
            raise ResourceIOError

    def writeString(self, srcData, dstPrefix, dstFile, overwrite=True):
        """Upload file to OSS with prefix dstPath."""
        mime_type = 'application/octet-stream'
        dstFilePath = os.path.join(dstPrefix, dstFile)
        try:
            res = self.oss.put_object_from_string(
                self.oss_bucket,
                dstFilePath,
                srcData,
                content_type=mime_type
            )
            if res.status != 200:
                logging.error('Fail to save string data to OSS: %s\n%s',
                              res.status, res.read())
                raise ResourceIOError(
                    'Fail to save string to OSS [%s]' % dstFilePath
                )
        except HTTPException, e:
            logging.error(
                'Fail to save string to OSS [%s]', dstFilePath, exc_info=True
            )
            raise VendorConnectionError
        except IOError, e:
            logging.error(
                'Fail to save string to OSS [%s]', dstFilePath, exc_info=True
            )
            raise ResourceIOError(
                'Fail to save string to OSS [%s]' % dstFilePath
            )

    def readFile(self, srcPrefix, srcFile, dstPath, dstFile):
        """Download file srcPath from OSS to dstPath."""
        srcFilePath = os.path.join(srcPrefix, srcFile)
        dstFilePath = os.path.join(dstPath, dstFile)
        print 'READ srcFilePath:%s' % srcFilePath
        print 'READ dstFilePath:%s' % dstFilePath
        try:
            res = self.oss.get_object_to_file(
                self.oss_bucket, srcFilePath, dstFilePath
            )
            print 'READ %s\n%s' % (res.status, res.read())
            if res.status != 200:
                if res.status == 404:
                    raise ResourceMissing(
                        'File [%s] not exists in OSS' % srcFilePath
                    )
                else:
                    logging.error(
                        'Get file [%s] [%s] from OSS failed:%s',
                        srcFilePath, res.status, res.read()
                    )
                    raise ResourceIOError(
                        'Fail to get file from OSS [%s]' % srcFilePath
                    )
        except HTTPException:
            logging.error(
                'Fail to get file from OSS [%s]', srcFilePath, exc_info=True
            )
            raise VendorConnectionError
        except IOError:
            logging.error(
                'Fail to get file from OSS [%s]', srcFilePath, exc_info=True
            )
            raise ResourceIOError

    def readFileContent(self, srcPrefix, srcFile):
        """Get file content from OSS to dstPath."""
        srcFilePath = os.path.join(srcPrefix, srcFile)
        print 'READ srcFilePath:%s' % srcFilePath
        try:
            res = self.oss.get_object(
                self.oss_bucket, srcFilePath
            )
            fileContent = res.read()
            print 'READ %s\n%s' % (res.status, fileContent)
            if res.status != 200:
                if res.status == 404:
                    raise ResourceMissing(
                        'File [%s] not exists in OSS' % srcFilePath
                    )
                else:
                    logging.error(
                        'Get file [%s] [%s] from OSS failed:%s',
                        srcFilePath, res.status, res.read()
                    )
                    raise ResourceIOError(
                        'Fail to get file from OSS [%s]' % srcFilePath
                    )
        except HTTPException:
            logging.error(
                'Fail to get file from OSS [%s]', srcFilePath, exc_info=True
            )
            raise VendorConnectionError
        except IOError:
            logging.error(
                'Fail to get file from OSS [%s]', srcFilePath, exc_info=True
            )
            raise ResourceIOError

        return fileContent

    def deleteFile(self, srcPrefix, srcFile):
        """Delete file path in OSS."""
        srcFilePath = os.path.join(srcPrefix, srcFile)
        try:
            res = self.oss.delete_object(self.oss_bucket, srcFilePath)
            if res.status not in [200, 204, 404]:
                logging.error('Delete file [%s] from OCS failed:[%s]%s',
                              srcFilePath, res.status, res.read())
                raise ResourceIOError(
                    'Delete file [%s] from OCS failed' % srcFilePath
                )
        except HTTPException:
            logging.error(
                'Delete file [%s] from OCS failed', srcFilePath, exc_info=True
            )
            raise VendorConnectionError

    def deleteFiles(self, srcPrefix):
        """Delete all files with prefix."""
        try:
            return delete_all_objects(self.oss, self.oss_bucket, srcPrefix)
        except HTTPException:
            logging.error(
                'Delete files with prefix [%s] from OCS failed',
                srcPrefix, exc_info=True
            )
            raise VendorConnectionError


if __name__ == '__main__':
    conf = {
        'id': 2,
        'type': 'aliyun',
        'url': 'oss.aliyuncs.com',
        'bucket': 'cloudraid1',
        'access_key': 'EWzLNAoSdqewWCgT',
        'access_secret': 'vDXZzRzz1O1syJRC2oUb93ztVMGfkH'
    }
    aliyun = AliyunStorage(**conf)
    aliyun.deleteFiles('1')
    #aliyun.writeFile('/tmp/test.log', 'test.log')
    #aliyun.downloadFile(None, None, '/home/garry/test.log')
