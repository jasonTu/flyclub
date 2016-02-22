#coding: utf-8

import os
import logging
import requests
import traceback

import qiniu.conf
import qiniu.rs
import qiniu.io
import qiniu.resumable_io as rio

from common.constants import VENDOR_TYPE_QINIU

from storage import Storage


class QiniuStorage(Storage):
    __vendor_type__ = VENDOR_TYPE_QINIU

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        qiniu.conf.ACCESS_KEY = kwargs.get('access_key')
        qiniu.conf.SECRET_KEY = kwargs.get('access_secret')
        self.bucket_name = kwargs.get('bucket')
        self.domain = kwargs.get('url')

    @classmethod
    def getStorageInfo(cls):
        return {
            'vendor': cls.__vendor_type__,
        }

    def writeFile(self, srcPath, dstPath, overWrite=True):
        policy = qiniu.rs.PutPolicy(self.bucket_name)
        extra = rio.PutExtra(self.bucket_name)
        path = os.path.join(os.path.dirname(dstPath),
                            os.path.basename(srcPath))
        print path
        try:
            _, err = rio.put_file(policy.token(), path, srcPath, extra)
            if err is not None:
                logging.error('Upload qiniu file [%s] failed:%s', srcPath, err)
                return False
        except:
            logging.error(traceback.format_exc())
            return False
        return True

    def readFile(self, srcPath, dstPath):
        path = os.path.join(dstPath, os.path.basename(srcPath))
        print path
        base_url = qiniu.rs.make_base_url(self.domain, srcPath)
        print base_url
        try:
            resp = requests.get(base_url)
            if resp.status_code == 200:
                with open(path, 'w') as f:
                    f.write(resp.content)
                    return True
        except:
            traceback.print_exc()
            logging.error(traceback.format_exc())
        return False

    def deleteFile(self, path):
        try:
            _, err = qiniu.rs.Client().delete(self.bucket_name, path)
            if err is None:
                return True
            else:
                logging.error('Delete file [%s] failed: %s ', path, err)
        except:
            logging.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    qn = QiniuStorage(**{
        'vname': 'qiniu',
        'url': 'doc-manager.qiniudn.com',
        'bucket': 'doc-manager',
        'access_key': 'QGvgzM1dGfOA5A8ExZL6UaZWh0NOjIb5zb85ZR-A',
        'access_secret': 'IoYWBGMeCD2qhFmkNg9imW5r04Ccm1G3lGNeuDbU',
        'access_token': '',
    })
    #qn.writeFile('/home/garry/Downloads/redis.mobi', 'garry/')
    #qn.readFile('garry/redis.mobi', '/tmp')
    qn.deleteFile('garry/redis.mobi')
