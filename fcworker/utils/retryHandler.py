# coding: utf-8
"""Commont retry API."""
import time
import logging
import traceback

import gevent

from exceptions import RecoverableException, UnRecoverableException


def retryExecute(callback, retryNumber, isGevent, sleepSeconds, **kwargs):
    """Retry in gevent mode."""
    retry = 0
    while retry < retryNumber:
        try:
            return callback(**kwargs)
        except RecoverableException, e:
            if isGevent:
                gevent.sleep(sleepSeconds * (2 ** retry))
            else:
                time.sleep(sleepSeconds * (2 ** retry))
            retry += 1
            if retry == retryNumber:
                raise e
