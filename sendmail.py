#!/usr/bin/python

"""
Send one cached file in `sendcache` and delete the mentioned file.


This piece of program fetchs the newest result existing in `sendcache` and
send it to mailing lists configured in `config/maillist-address` using SMTP
configurations defined by `config/smtp-server`, `config/smtp-username` and
`config/smtp-password`. Edit these files to input proper parameters.

Notice that parameters read from `config` path are trim'ed.
"""

import os
import sys

def getConf(name):
    return open(os.path.join('config', name), 'r').read().strip()


smtpServer = getConf('smtp-server')
smtpUsername = getConf('smtp-username')
smtpPassword = getConf('smtp-password')

receiversRaw = getConf('maillist-address').split('\n')
receivers = []
for each in receiversRaw:
    each = each.strip()
    if '' != each:
        receivers.append(each)

cacheListRaw = os.listdir('sendcache')

cacheList = []
removeList = []
for each in cacheListRaw:
    fullname = os.path.realpath(os.path.join('sendcache', each))
    if not os.path.isfile(fullname):
        continue
    if fullname.endswith('.7z'):
        cacheList.append(fullname)
    else:
        removeList.append(fullname)

cacheList.sort()

if len(cacheList) < 1:
    sys.exit(0)
targetFile = cacheList[-1]
removeList.append(targetFile)

print targetFile
