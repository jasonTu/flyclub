# coding: utf-8
"""Micro-backup exception hierachy."""


class MicroBackupException(Exception):

    """Base exceptions."""

    def __init__(self, message='', errors=None):
        super(MicroBackupException, self).__init__(message)


class UnRecoverableException(MicroBackupException):

    """Exceptions that need programmer involve."""

    def __init__(self, message='', errors=None):
        super(UnRecoverableException, self).__init__(message, errors)


class RecoverableException(MicroBackupException):

    """Exceptions that can retry."""

    def __init__(self, message='', errors=None):
        super(RecoverableException, self).__init__(message, errors)


class ResourceMissing(UnRecoverableException):

    """File missing which caused by bug or mis-operations."""

    def __init__(self, message='', errors=None):
        super(ResourceMissing, self).__init__(message, errors)


class ResourceFormatError(UnRecoverableException):

    """File format incorrect which caused by bug or mis-operations."""

    def __init__(self, message='', errors=None):
        super(ResourceFormatError, self).__init__(message, errors)


class VendorConnectionError(RecoverableException):

    """Connection error for download/upload file from/to vendors."""

    def __init__(self, message='', errors=None):
        super(VendorConnectionError, self).__init__(message, errors)


class ResourceIOError(RecoverableException):

    """Local File operation error."""

    def __init__(self, message='', errors=None):
        super(ResourceIOError, self).__init__(message, errors)
