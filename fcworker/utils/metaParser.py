# coding: utf-8
"""Micro-backup meta file parser."""

import zlib
import binascii
import StringIO

from common.constants import (
    META_FILE_TYPE_COMMIT,
    META_FILE_TYPE_TREE,
    META_FILE_TYPE_FILE,
    META_FILE_TYPE_RAID,
    META_FILE_TYPE_CACHE
)
from .binaryReader import BinaryReader


class MetaParser(object):

    """Base class of meta file parsers."""

    def __init__(self, filename):
        """Init biniary parser and decomress object."""
        self.fileHandle = open(filename, 'rb')
        self.rawReader = BinaryReader(self.fileHandle)
        self.dataReader = None
        self.decompressor = zlib.decompressobj()

    def getItems(self):
        """Return parsed data with genrator."""
        fileType, _ = self.rawReader.read('!2I')
        compressData = self.fileHandle.read()
        self.dataReader = BinaryReader(StringIO.StringIO(
            self.decompressor.decompress(compressData) +
            self.decompressor.flush()
        ))
        # fileType, contentLength
        fileType, _ = self.dataReader.read('!2I')
        if fileType in [META_FILE_TYPE_COMMIT,
                        META_FILE_TYPE_TREE,
                        META_FILE_TYPE_FILE,
                        META_FILE_TYPE_RAID]:  # commit/tree/file/raid
            return self.getMetaItem()
        elif fileType == META_FILE_TYPE_CACHE:
            return self.getCacheItem()

    def getMetaItem(self):
        """Get meta item with generator."""
        while True:
            line = self.dataReader.readline()
            if line:
                yield line.strip().split(' ')
            else:
                break

    def getCacheItem(self):
        """Get cache item with generator."""
        # _, version, count
        _, _, count = self.dataReader.read('!3I')
        for _ in xrange(count):
            item = list(self.dataReader.read('!10I20s20s2I'))
            fileName = self.dataReader.read(
                '{length}s'.format(length=item[-1] + 1)
            )
            item.append(fileName)
            # Convert fileSha1 from binary to hex string
            item[10] = binascii.b2a_hex(item[10])
            yield item

    def __del__(self):
        """Close the file."""
        self.fileHandle.close()


if __name__ == '__main__':
    # parser = MetaParser('./metas/aa546621a8bfa63c576b550792ddb27d32834369')
    parser = MetaParser('./metas/b74700d544485e8ac155128891083c637f5be94f')
    for it in parser.getItems():
        print it
