#!/usr/bin/python

"""
List available files at `mtsat-1r.cr.chiba-u.ac.jp`.
"""

from ftplib import FTP
import time
import sys

if len(sys.argv) < 2:
    sys.exit(1)
dateMonth = sys.argv[1]

ftp = FTP('mtsat-1r.cr.chiba-u.ac.jp')     # connect to host, default port
loginRet = ftp.login()                     # user anonymous, passwd anonymous
if loginRet.startswith('230'):
    ftp.cwd('grid-MTSAT-2.0/MTSAT2/%s' % dateMonth)               # change into "debian" directory
    ftp.dir() #retrlines('LIST')
else:
    sys.exit(1)

try:
    ftp.quit()
except:
    try:
        ftp.close()
    except:
        pass
