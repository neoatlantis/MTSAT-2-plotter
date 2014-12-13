#!/usr/bin/python

DATA_MAX = 5
MIRROR_MAX = 1

"""
Clean the site/data and site/mirror regularly to release space.
==============================================================

"""

import os
from subprocess import call
import sys
import time

sitePath = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), 'site')

dataPath = os.path.join(sitePath, 'data')
mirrorPath = os.path.join(sitePath, 'mirror')


removeList = []

def howOld(timeobj):
    nowtime = time.mktime(time.gmtime())
    compare = time.mktime(timeobj)
    return nowtime - compare

def filterOldFile(path, days):
    dataList = os.listdir(path)
    outList = []
    for filename in dataList:
        fileFullname = os.path.join(path, filename)
        filetime = False
        try:
            filetime = time.strptime(filename[0:12], '%Y%m%d%H%M')
        except:
            pass
        if filetime == False:
            try:
                filetime = time.gmtime(os.path.getmtime(fileFullname))
            except:
                pass
        if filetime:
            if howOld(filetime) > 86400 * days:
                outList.append(fileFullname)
    return outList



if os.path.isdir(dataPath):
    dataOldList = filterOldFile(dataPath, DATA_MAX)
    removeList += dataOldList

if os.path.isdir(mirrorPath):
    mirrorOldList = filterOldFile(mirrorPath, MIRROR_MAX)
    removeList += mirrorOldList


doRemove = False
if len(sys.argv) >= 2:
    doRemove = (sys.argv[1] == 'REMOVE')

if not doRemove:
    print "This is only a test. Use `./003-cleaner.py REMOVE` to fire actual removing actions."

removeCommands = [['rm', '-rf', i] for i in removeList]
for command in removeCommands:
    print ' '.join(command)
    if doRemove:
        call(command)
