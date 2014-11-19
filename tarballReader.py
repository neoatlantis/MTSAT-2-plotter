#!/usr/bin/python

"""
Reads the .tar.bzip file provided by offical FTP
"""

import tarfile
import sys

try:
    tar = tarfile.open(sys.argv[1], 'r:bz2')
except:
    sys.exit(1)

print "> Reading the content of tarball..."

tarInfos = tar.getmembers()

print "> Got %d files." % len(tarInfos)

for each in tarInfos:
    print each.name, each.size
