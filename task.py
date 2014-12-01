#!/usr/bin/python

"""
Read updated mirror, and create tasks for new IR data.
"""

import time
import os
import subprocess
import sys

startTime = time.time()

try:
    DATEMONTH = sys.argv[1]
    currentPath = os.path.realpath(os.path.dirname(sys.argv[0]))

    mirrorPathBase = os.path.join(currentPath, 'site', 'mirror', DATEMONTH)
    dirList = os.listdir(mirrorPathBase)
    
    mirrorList = []
    for each in dirList:
        if each.endswith('.tar.bz2'):
            mirrorList.append(each)

    outputPathBase = os.path.join(currentPath, 'site', 'data', DATEMONTH)
    logFilePath = os.path.join(outputPathBase, 'log.txt')
except:
    exit(1)

for each in mirrorList:
    outputPath = os.path.join(outputPathBase, each[:-8])
    sendcacheFile = os.path.join(currentPath, 'sendcache', each[:-8] + '.7z')

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
        mirrorPath = os.path.join(mirrorPathBase, each)

        print "Treating tarball [%s], saving to [%s]..." % (mirrorPath, outputPath)
        subprocess.call(['python', 'reader.py', mirrorPath, outputPath, logFilePath])

        """
        print "Compressing result(s) for mailing..."
        resultListRaw = os.listdir(outputPath)
        commandList = ['7za', 'a', sendcacheFile]
        for each in resultListRaw:
            if each.endswith('.png') or each.endswith('.jpg'):
                commandList.append(os.path.join(outputPath, each))
        subprocess.call(commandList)
        """

        nowTime = time.time()
        if nowTime - startTime > 600:
            exit(0)
