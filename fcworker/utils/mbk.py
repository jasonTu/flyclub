# coding: utf-8
"""View mbk files."""
import sys
import zlib
import struct
import binascii
import StringIO

fileTypes = {
    4: 'Commit Object',
    5: 'Tree Object',
    6: 'File Object',
    7: 'Raid Object',
    8: 'Blob Object',
    9: 'Cache Object'
}


def metaProcess(fileHandle):
    """Meta file process include 4, 5, 6, 7."""
    for line in fileHandle.readlines():
        print line.strip()


def cacheProcess(fileHandle):
    """Cache file process 9."""
    typeFormat = '!3I'
    typeSize = struct.calcsize(typeFormat)
    _, version, count = struct.unpack(typeFormat, fileHandle.read(typeSize))
    print 'Version [%d], item count: [%d]' % (version, count)

    typeFormat = '!10I20s20s2I'
    typeSize = struct.calcsize(typeFormat)
    for i in xrange(count):
        items = list(struct.unpack(typeFormat, fileHandle.read(typeSize)))
        items[10] = binascii.b2a_hex(items[10])
        items[11] = binascii.b2a_hex(items[11])
        fileNameLength = items[-1] + 1
        (fileName, ) = struct.unpack(
            '%ss' % fileNameLength, fileHandle.read(fileNameLength)
        )
        items.append(fileName)
        print items
        #print [items[12], items[10], items[14]]


def fileProcess(filePath):
    """Parse mbk files."""
    with open(filePath, 'rb') as f:
        typeFormat = '!2I'
        typeSize = struct.calcsize(typeFormat)
        fileType, length = struct.unpack(typeFormat, f.read(typeSize))
        print fileTypes[fileType]
        print 'File type:[%d], content length:[%d]' % (fileType, length)
        content = f.read()
        decompressor = zlib.decompressobj()
        rawContent = decompressor.decompress(content)
        rawContent += decompressor.flush()
        fs = StringIO.StringIO(rawContent)
        fileType, length = struct.unpack(typeFormat, fs.read(typeSize))
        print 'Compressed file type:[%d], content length:[%d]' % (
            fileType, length
        )
        print '=============================================='
        if fileType in [4, 5, 6, 7]:
            metaProcess(fs)
        if fileType == 9:
            cacheProcess(fs)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: python mbk.py filename'
        sys.exit(1)
    fileProcess(sys.argv[1])
