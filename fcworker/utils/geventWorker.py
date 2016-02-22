# coding: utf-8
"""Backup/Restore base worker."""
import gevent
from gevent import Greenlet

from utils.exceptions import MicroBackupException


class GeventWorker(Greenlet):

    """Restore worker base class."""

    def __init__(self):
        """Register greenlet."""
        Greenlet.__init__(self)
        self.__class__.worker_greenlets.append(self)

    @classmethod
    def launchGreenlets(cls, number, **kwargs):
        """Launch greenlets in batch."""
        for i in xrange(number):
            kwargs.update({'gid': i})
            glets = cls(**kwargs)
            glets.start()

    @classmethod
    def resetGreenlets(cls):
        """Status reset."""
        while not cls.work_queue.empty():
            cls.work_queue.get()
        if hasattr(cls, 'work_set'):
            cls.work_set.clear()
        cls.worker_greenlets[:] = []
        if hasattr(cls, 'reset'):
            cls.reset()

    @classmethod
    def killAllGreenlets(cls, exception=gevent.GreenletExit):
        """Kill all current greenlets."""
        gevent.killall(cls.worker_greenlets, exception)

    @classmethod
    def joinAllGreenlets(cls):
        """Kill all current greenlets."""
        gevent.joinall(cls.worker_greenlets)
        for greenlet in cls.worker_greenlets:
            if greenlet.value is None:
                # Raise exception raised in greenlets
                greenlet.get()
        return True

    @classmethod
    def pushTask(cls, task, key=None):
        """Put task into child class work queue."""
        if hasattr(cls, 'work_set'):
            if key is None:
                key = task
            if key not in cls.work_set:
                cls.work_queue.put(task)
                cls.work_set.add(key)
        else:
            cls.work_queue.put(task)

    @classmethod
    def getTask(cls):
        """Get task from child class work queue."""
        return cls.work_queue.get()
