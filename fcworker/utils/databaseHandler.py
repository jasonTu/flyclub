# coding: utf-8
"""APIs to interacte with databases."""

import os
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mbkserver.settings")

import django
from django.db import transaction
from django.utils import timezone
from cassandra.cqlengine import connection
from cassandra.cqlengine.functions import MinTimeUUID

django.setup()

from mbkuser.models import MbkQuotaInfo
from failtask.models import MbkFailTask
from mstorage.models import StorageCredential
from mbkdevice.models import MbkDeviceTask, MbkDevice
from common.constants import (
    TASK_STATUS_IDLE, BACKUP_STATUS_SUCCEED,
    KEEP_LAST_ONE_WEEK, KEEP_LAST_TWO_WEEKS,
    KEEP_LAST_ONE_MONTH, KEEP_LAST_THREE_MONTHS,
    KEEP_LAST_SIX_MONTHS, KEEP_LAST_ONE_YEAR,
)
from mbackup.casModel import BackupDeltaBank
from mbackup.models import MbkBackupInfo, MbkRestoreInfo
from mbkuser.models import MbkQuotaInfo, MbkUser

from .storageManager import StorageManager
from .configManager import cassandraConfig

INIT_CASSANDRA = False


def initCassandraConnection():
    """Cassandra connection init."""
    global INIT_CASSANDRA
    if not INIT_CASSANDRA:
        connection.setup(
            cassandraConfig['nodes'].split(','), cassandraConfig['keySpace']
        )
        INIT_CASSANDRA = True


def getBackupTaskWorkLoads(bkid):
    """Get work loads according to commit id."""
    try:
        backupInfo = MbkBackupInfo.objects.values(
            'content', 'is_done'
        ).get(pk=bkid)
    except MbkBackupInfo.DoesNotExist:
        logging.error('Backup task [%d] is not existed.', bkid)
        return None
    if backupInfo['is_done']:
        logging.error('Backup task [%d] is already done.', bkid)
        return None
    content = json.loads(backupInfo['content'])
    if content and 'metas' in content and 'blobs' in content:
        return content
    return None


def getStorageAccess(uid):
    """Get storage credentials."""
    storageAccess = []
    try:
        credentials = StorageCredential.objects.select_related('vendor').filter(
            user__id=uid, is_active=True
        )
        if not credentials:
            # TODO: Cache system credentials
            credentials = StorageCredential.objects.select_related(
                'vendor'
            ).filter(
                is_sys=True, is_active=True
            )
    except:
        logging.error('Get credentials failed.', exc_info=True)
        return None
    for cred in credentials:
        params = {
            'id': cred.id,
            'priority': cred.priority,
            'vtype': cred.vendor.vtype,
            'url': cred.vendor.access_url,
        }
        params.update(cred.credentials)
        storageAccess.append(params)
    return storageAccess


def getStorageAccessObjects(uid):
    """Get credentials and build storage access object."""
    storageAccess = getStorageAccess(uid)
    if storageAccess is None:
        return None, None
    accessObjs = [
        StorageManager.buildStorageVendorInstance(**storage)
        for storage in storageAccess
    ]
    accessObjs.sort(key=lambda obj: obj.priority, reverse=True)
    return accessObjs, storageAccess


def getStorageAccessObjectsByBackupId(bkid):
    """Get storage access with bkid."""
    storageAccess = []
    try:
        mbkInfo = MbkBackupInfo.objects.get(pk=bkid)
    except MbkBackupInfo.DoesNotExist:
        return None, None
    for cred in mbkInfo.credentials_map.all():
        params = {
            'id': cred.id,
            'priority': cred.priority,
            'vtype': cred.vendor.vtype,
            'url': cred.vendor.access_url,
        }
        params.update(cred.credentials)
        storageAccess.append(params)
    accessObjs = [
        StorageManager.buildStorageVendorInstance(**storage)
        for storage in storageAccess
    ]
    accessObjs.sort(key=lambda obj: obj.priority, reverse=True)
    return accessObjs, storageAccess


def setBackupInfoDone(bkid, credentials):
    """Update backupInfo when backup is done."""
    now = timezone.now()
    with transaction.atomic():
        backupInfo = MbkBackupInfo.objects.get(pk=bkid)
        backupInfo.credentials_map.add(*[cred['id'] for cred in credentials])
        MbkBackupInfo.objects.filter(pk=bkid).update(
            is_done=True, date_backuped=now, status=BACKUP_STATUS_SUCCEED
        )
        device = backupInfo.task.device
        device.last_backuped = datetime.fromtimestamp(
            backupInfo.statistics['backup_date']
        )
        device.save()


def updateBackupInfoStatistics(bkid, statistics):
    """Update backup statistics."""
    backupInfo = MbkBackupInfo.objects.get(pk=bkid)
    stat = backupInfo.statistics
    for k, v in statistics.iteritems():
        stat[k] = stat.get(k, 0) + v
    backupInfo.statistics = stat
    backupInfo.save()


def finishBackupInfo(bkid, status, syncTag, commit, statistics):
    """Update backup info with commit and statistics."""
    now = timezone.now()
    with transaction.atomic():
        backupInfo = MbkBackupInfo.objects.get(pk=bkid)
        MbkBackupInfo.objects.filter(pk=bkid).update(
            is_done=True, date_backuped=now, statistics=statistics,
            status=status, commit=commit
        )
        task = backupInfo.task
        task.status = TASK_STATUS_IDLE
        if syncTag is not None:
            task.sha1_synctag = syncTag
        task.save()
        device = backupInfo.device
        device.last_backuped = datetime.fromtimestamp(
            statistics.get('backup_date', time.mktime(now.timetuple()))
        )
        device.save()


def updateBackupDirLayout(bkid, layout):
    """Update dir layout of specific backup for portal."""
    MbkBackupInfo.objects.filter(pk=bkid).update(dir_layout=layout)


def getBackupCommit(bkid):
    """Get backup."""
    try:
        mbkInfo = MbkBackupInfo.objects.values('commit').get(id=bkid)
    except MbkBackupInfo.DoesNotExist:
        return None
    return mbkInfo['commit']


def getNextBackupCommit(did, bkid):
    """Get next adjancent backup."""
    try:
        mbkInfo = MbkBackupInfo.objects.values('commit').filter(
            device__id=did, id__gt=bkid
        )[0]
    except IndexError:
        return None
    return mbkInfo['commit']


def isRestoreTaskOK(restoreId):
    """Check restore task is ok to processd."""
    try:
        restoreInfo = MbkRestoreInfo.objects.values(
            'is_done'
        ).get(pk=restoreId)
    except MbkRestoreInfo.DoesNotExsit:
        logging.error('Restore task is not existed.')
        return False
    if restoreInfo['is_done']:
        logging.error('Restore task [%d] is already done.', restoreId)
        return False
    return True


def setRestoreInfoDone(restoreId):
    """Update restoreInfo when restore data is ready."""
    now = timezone.now()
    with transaction.atomic():
        MbkRestoreInfo.objects.filter(pk=restoreId).update(
            is_done=True, date_ready=now
        )
        # Update last restore time, too complicate now...
        bk = MbkRestoreInfo.objects.values('backupInfo').get(pk=restoreId)
        backupInfo = MbkBackupInfo.objects.get(pk=bk['backupInfo'])
        device = backupInfo.task.device
        device.last_restored = now
        device.save()


def saveFailedTask(task, task_type, callstack):
    """Save failed task for programmer."""
    ftask = MbkFailTask(
        task_type=task_type, fail_date=timezone.now(),
        task_content=task, fail_callstack=callstack
    )
    ftask.save()


def getExpiredBackups(taskId, userId):
    """Get backups need to be purged according to purge type."""
    retList = []
    try:
        taskInfo = MbkDeviceTask.objects.get(pk=taskId, device__user__id=userId)
    except MbkDeviceTask.DoesNotExist:
        logging.error('Task [%d] is not existed.', taskId)
        return retList
    purgeType = taskInfo.purge_type
    if purgeType == KEEP_LAST_ONE_WEEK:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=7-1)
    elif purgeType == KEEP_LAST_TWO_WEEKS:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=14-1)
    elif purgeType == KEEP_LAST_ONE_MONTH:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=31-1)
    elif purgeType == KEEP_LAST_THREE_MONTHS:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=92-1)
    elif purgeType == KEEP_LAST_SIX_MONTHS:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=183-1)
    elif purgeType == KEEP_LAST_ONE_YEAR:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=365-1)
    else:
        expiredTime = timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=92-1)
    try:
        expiredBackups = MbkBackupInfo.objects.filter(
            task=taskInfo,
            date_backuped__lt=expiredTime
        ).order_by('date_backuped')
    except:
        logging.error('Get expiredBackups failed.', exc_info=True)
        return retList

    for expiredBackup in expiredBackups:
        retList.append(expiredBackup.id)
    return retList


def getBackup(backupId, userId):
    """Get backupInfo."""
    try:
        info = MbkBackupInfo.objects.get(id=backupId, device__user__id=userId)
        return info
    except MbkBackupInfo.DoesNotExist:
        return None


def deleteBackup(info):
    """Delete backupInfo."""
    info.delete()


def updatePurgeQuotaInfo(task):
    """Update quotainfo after after pushing purge task."""
    uid = task['uid']
    did = task.get('did', None)
    tid = task.get('tid', None)
    bid = task.get('bid', None)
    # print (
    #     "Purge task is doing, task: %s" % (json.dumps(task, indent=4))
    # )
    # backup
    if bid is not None:
        device = 0
        try:
            backupInfo = MbkBackupInfo.objects.get(
                id=bid, device__user__id=uid
            )
            size = backupInfo.statistics['transed_size']
        except MbkBackupInfo.DoesNotExist:
            size = 0
    # task
    elif tid is not None:
        device = 0
        try:
            backupInfo = MbkBackupInfo.objects.filter(
                task__id=tid, device__user__id=uid
            )
            size = 0
            for backupinfo in backupInfo:
                size += backupinfo.statistics['transed_size']
        except MbkBackupInfo.DoesNotExist:
            size = 0
    # device
    elif did is not None:
        device = 1
        try:
            backupInfo = MbkBackupInfo.objects.filter(
                device__id=did, device__user__id=uid
            )
            size = 0
            for backupinfo in backupInfo:
                size += backupinfo.statistics['transed_size']
        except MbkBackupInfo.DoesNotExist:
            size = 0
    # user
    else:
        try:
            backupInfo = MbkBackupInfo.objects.filter(device__user__id=uid)
            size = 0
            for backupinfo in backupInfo:
                size += backupinfo.statistics['transed_size']
            deviceInfo = MbkDevice.objects.filter(user__id=uid)
            device = len(deviceInfo)
        except MbkBackupInfo.DoesNotExist:
            size = 0
            device = 0
    if size or device:
        print ("Purge total size %d." % (size))
        print ("Purge total device number: %d." % (device))
    # update user quota and device
    user = MbkUser.objects.get(pk=uid)
    with transaction.atomic():
        device = -device
        size = -size
        user.updateDeviceUsed(device)
        user.updateQuotaUsed(size)


# Backup delta process
def updateBackupDeltaBank(tid, bkid):
    """Add backup delta after backup is deleted."""
    initCassandraConnection()
    BackupDeltaBank.create(tid=tid, tkey=uuid.uuid1(), bid=bkid)


def getBackupDeltas(tid, timeuuid):
    """Return deltas of specific time to now."""
    initCassandraConnection()
    if timeuuid is None:
        minTime = datetime(1979, 1, 1)
        items = BackupDeltaBank.objects.filter(
            tid=tid, tkey__gte=MinTimeUUID(minTime)
        ).values_list('tkey', 'bid')
    else:
        items = BackupDeltaBank.objects.filter(
            tid=tid, tkey__gte=timeuuid).values_list('tkey', 'bid')
    return items
