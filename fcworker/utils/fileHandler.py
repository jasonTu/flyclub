# coding: utf-8
"""Temp files handlers."""
import os
import glob


def tempDirCleanup(tmpDir):
    """Clean files in temp dir and remove the dir."""
    for filePath in glob.glob(os.path.join(tmpDir, '*')):
        os.remove(filePath)
    os.rmdir(tmpDir)
