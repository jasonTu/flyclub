# coding: utf-8
"""Binary file reader according to format."""

import struct


class BinaryReaderEOFException(Exception):

    """EOF Exception."""

    def __init__(self):
        pass

    def __str__(self):
        return 'Not enough bytes in file to satisfy read request'


class BinaryReader(object):

    def __init__(self, fileHandle):
        self.file = fileHandle

    def read(self, typeFormat):
        """Paramter typeName can be predefined type or format string."""
        typeSize = struct.calcsize(typeFormat)
        value = self.file.read(typeSize)
        if typeSize != len(value):
            raise BinaryReaderEOFException
        return struct.unpack(typeFormat, value)

    def readline(self):
        return self.file.readline()
