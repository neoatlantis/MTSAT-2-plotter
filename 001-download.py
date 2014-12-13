#!/usr/bin/python

import os
import sys
import subprocess
import time
import re

dateMonth = time.strftime('%Y%m', time.gmtime())

FTPBASE = 'ftp://mtsat-1r.cr.chiba-u.ac.jp/grid-MTSAT-2.0/MTSAT2/' + dateMonth
BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
OUTPUTPATH = os.path.join(BASEPATH, 'site', 'mirror')
MAXTIME = 1200 # MAX run time, approx.

try:
    os.makedirs(OUTPUTPATH)
except:
    pass

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


##############################################################################

pattern = re.compile("^[0-9]{12}\.(vis|ir)\.tar\.bz2$")

gotlist = []
for each in ftplist:
    parts = each.split(' ')
    if len(parts) > 0:
        filename = parts[-1].strip()
        if None != pattern.match(filename):
            gotlist.append(filename)


mirrorList = filterNewFile(gotlist, 1)
targetList = os.listdir(OUTPUTPATH)

downloadList = []

print "> Check mirror directory and decide download list..."
for filename in mirrorList:
    if filename in targetList:
        print ">> Skip file: %s" % filename
        continue
    downloadList.append(filename)

print "> Begin downloading..."
starttime = time.time()
for filename in downloadList:
    outputFilename = os.path.join(OUTPUTPATH, filename)
    outputFilenameTemp = outputFilename + '.tmp'
    cmd = [\
        'wget',
        '-c',           # continue download
        '-U',
        'Mozilla/5.0 (compatible; NeoAtlantis MTSAT-2 Satellite Image Service; +http://mtsat-2.neoatlantis.org/)',
        '-o',
        '/dev/null',    # no log recorded
        '-O',
        outputFilenameTemp,
        FTPBASE + '/' + filename,
    ]
    nowtime = time.time()
    if nowtime - starttime > MAXTIME:
        print "> Download have costed enough time. Exit now."
        break
    try:
        print "> Download file: %s" % (FTPBASE + '/' + filename)
        ret = subprocess.call(cmd)
    except Exception,e:
        continue
    if 0 == ret:
        os.rename(outputFilenameTemp, outputFilename)
    time.sleep(5)

print "> Finish."
