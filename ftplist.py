#!/usr/bin/python

"""
List available files at `mtsat-1r.cr.chiba-u.ac.jp`.
"""

import time
import sys
import re

from ftplib import FTP

if \
    len(sys.argv) < 3 or\
    not re.match('^[0-9]{6}$', sys.argv[1]) or\
    not sys.argv[2] in ['EXT', 'SIR', 'TIR', 'VIS']:
    
    print "Usage: python ftplist.py <YYYYMM> <EXT|SIR|TIR|VIS>"
    sys.exit(1)
dateMonth = sys.argv[1]
channel = sys.argv[2]

ftp = FTP('hmwr829gr.cr.chiba-u.ac.jp')     # connect to host, default port
loginRet = ftp.login()                     # user anonymous, passwd anonymous
if loginRet.startswith('230'):
    ftp.cwd('gridded/FD/V20151105/%s/%s' % (dateMonth, channel))
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
