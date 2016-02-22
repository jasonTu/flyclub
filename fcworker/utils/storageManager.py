#!/bin/env python
# coding: utf-8
"""Manager storage upload/download."""


class StorageManager(object):

    """Manager of all storage access classes."""

    storage_class_manager = {}
    is_manager_initialized = False

    @classmethod
    def registerStorageVendor(cls, *modules):
        """Register storage access module through vertor type."""
        for module in modules:
            cls.storage_class_manager[module.__vendor_type__] = module

    @classmethod
    def buildStorageVendorInstance(cls, **kwargs):
        """Parameter kwargs includes storage credential information."""
        storagecls = cls.storage_class_manager[kwargs.get('vtype')]
        return storagecls(**kwargs)


def initStorageManager():
    """Register all storage access classes."""
    if not StorageManager.is_manager_initialized:
        # Make vendor code together
        from .aliyun import AliyunStorage
        # from .qiniuyun import QiniuStorage

        StorageManager.registerStorageVendor(*[
            AliyunStorage,
            # QiniuStorage,
        ])
        StorageManager.is_manager_initialized = True

initStorageManager()
