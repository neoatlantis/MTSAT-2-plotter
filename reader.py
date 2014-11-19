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
print "> Analyze contents."

geossFile = []
for each in tarInfos:
    if each.name.endswith('.geoss'):
        if each.size == 18000000:
            geossFile.append(each)

print "> Found %d possible .geoss file." % len(geossFile)
print "> Generating commands for plotting geoss files..."

for each in geossFile:
    IR = each.name[10]
    DK = each.name[7]
    time = each.name[12:24]
    print IR, DK, time
