#!/usr/bin/python

import os
import sys
import subprocess
import time
import re

dateMonth = time.strftime('%Y%m', time.gmtime())

BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
OUTPUTPATH = os.path.join(BASEPATH, 'site', 'mirror', dateMonth)

def howOld(timeobj):
    nowtime = time.mktime(time.gmtime())
    compare = time.mktime(timeobj)
    return nowtime - compare

def filterNewFile(dataList, days):
    outList = []
    for filename in dataList:
        filetime = False
        try:
            filetime = time.strptime(filename[0:12], '%Y%m%d%H%M')
        except:
            pass
        if filetime:
            if howOld(filetime) < 86400 * days:
                outList.append(filename)
    return outList



try:
    print '> Begin connect to ftp server and retrieve the list.'
    ftplist = subprocess.check_output(['python', 'ftplist.py', dateMonth])
except:
    print "> Download error. Exit now."
    sys.exit(1)

ftplist = ftplist.split('\n')
print "> Got total %d files." % len(ftplist)

gotlist = []

pattern = re.compile("^[0-9]{12}\.(vis|ir)\.tar\.bz2$")
for each in ftplist:
    parts = each.split(' ')
    if len(parts) > 0:
        filename = parts[-1].strip()
        if None != pattern.match(filename):
            gotlist.append(filename)

mirrorList = [os.path.join(OUTPUTPATH, i) for i in filterNewFile(gotlist, 1)]
print mirrorList
