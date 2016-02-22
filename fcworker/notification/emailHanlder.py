# coding: utf-8
"""Emaiil worker."""

import os
import sys
sys.path.extend(['/opt/mbk/mbkworker', '/opt/mbk/mbkserver'])
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mbkserver.settings")

import logging
import requests

import django
from django.core.mail import EmailMessage, send_mail, BadHeaderError

django.setup()

from celery import Celery

from utils.configManager import broker


mailApp = Celery('emailHanlder', broker=broker)
mailApp.config_from_object('celeryconfig')


@mailApp.task(
    name='email.emailHanlder.mbk_emailHanlder',
    default_retry_delay=180,
    bind=True
)
def mbk_emailHanlder(self, message):
    """Send email to client."""
    print message
    # to must be a list
    subject, body, fromAddr, toAddr = (
        message['subject'], message['body'], message['from'], message['to']
    )
    cc = message.get('cc', None)
    bcc = message.get('bcc', None)
    # need add attachment support here
    msg = EmailMessage(subject, body, fromAddr, toAddr, bcc=bcc, cc=cc)
    msg.content_subtype = message.get('content_subtype', 'plain')

    try:
        msg.send(fail_silently=False)
    except BadHeaderError:
        logging.error('Send email failed: invalid header found.', exc_info=True)
        try:
            self.retry()
        except self.MaxRetriesExceededError:
            logging.error('Task failed after serveral times retry, '
                          'need programmer to involve.', exc_info=True)
            # TODO: Push into pending queue
    except Exception:
        logging.error(
            'Unknown exception happened, need programmer to involve.',
            exc_info=True
        )
        # TODO: Push into pending queue


def testSendEmail():
    send_mail('Subject', 'Message.', 'jason@puyacn.com', ['jason@puyacn.com'])

if __name__ == '__main__':
    testSendEmail()
