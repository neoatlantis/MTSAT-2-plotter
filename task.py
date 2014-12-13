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
    currentPath = os.path.realpath(os.path.dirname(sys.argv[0]))

    mirrorPathBase = os.path.join(currentPath, 'site', 'mirror')
    dirList = os.listdir(mirrorPathBase)
    
    mirrorList = []
    for each in dirList:
        if each.endswith('.tar.bz2'):
            mirrorList.append(each)

    outputPath = os.path.join(currentPath, 'site', 'data')
except:
    exit(1)

if not os.path.exists(outputPath):
    os.makedirs(outputPath)

outpathDir = os.listdir(outputPath)

for each in mirrorList:
    done = False
    for filename in outpathDir:
        if filename.startswith(each[0:12]):
            done = True
            break
    if done:
        print "Skip dealing with [%s]." % each
        continue

    mirrorPath = os.path.join(mirrorPathBase, each)

    print "Treating tarball [%s], saving to [%s]..." % (mirrorPath, outputPath)
    subprocess.call(['python', 'reader.py', mirrorPath, outputPath])

    nowTime = time.time()
    if nowTime - startTime > 600:
        exit(0)
