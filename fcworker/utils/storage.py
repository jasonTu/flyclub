# coding: utf-8


class Storage(object):
    def readFile(self, srcPath, dstPath):
        raise NotImplementedError

    def writeFile(self, srcPath, dstPath, overWrite=True):
        raise NotImplementedError

    def deleteFile(self, path):
        raise NotImplementedError

    def getStorageInfo(self):
        raise NotImplementedError
