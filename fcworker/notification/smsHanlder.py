# coding: utf-8
"""SMS worker."""
import sys
sys.path.extend(['/opt/mbk/mbkworker', '/opt/mbk/mbkserver'])

import logging
import hashlib
import requests
from celery import Celery

from utils.configManager import (broker, smsConfig)


smsApp = Celery('smsHanlder', broker=broker)
smsApp.config_from_object('celeryconfig')


@smsApp.task(
    name='sms.smsHanlder.mbk_smsHanlder',
    max_retries=3,
    default_retry_delay=30,
    bind=True
)
def mbk_smsHanlder(self, phones, content, signStr='【微备份】'):
    """Send SMS to phones."""
    _sysCharset = sys.getfilesystemencoding()
    message = (signStr+content).decode(_sysCharset).encode('gbk')

    _md5 = hashlib.md5()
    _md5.update(smsConfig['password'])
    psd = _md5.hexdigest()

    params = {
        'userId': smsConfig['user'],
        'password': psd,
        'mobile': phones,
        'content': message
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }

    try:
        response = requests.post(
            smsConfig['url'],
            data=params,
            headers=headers,
            timeout=smsConfig['timeout']
        )
        print 'sms.send.http.status =%d' % response.status_code
        if response.status_code == 200:
            responseStr = response.content.decode('gbk').encode(_sysCharset)
            print responseStr
        else:
            try:
                self.retry()
            except self.MaxRetriesExceededError:
                logging.error('Task failed after serveral times retry, '
                              'need programmer to involve.', exc_info=True)

    except requests.exceptions.Timeout:
        try:
            self.retry()
        except self.MaxRetriesExceededError:
            logging.error('Task failed after serveral times retry, '
                          'need programmer to involve.', exc_info=True)
