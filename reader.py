#!/usr/bin/python

"""
Reads the .tar.bzip file provided by offical FTP
"""

import sys
import tarfile
from plot import plotter, convert # TODO read convert table

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
        if each.size == 18000000 or each.size == 288000000:
            geossFile.append(each)

print "> Found %d possible .geoss file." % len(geossFile)
print "> Generating commands for plotting geoss files..."

for each in geossFile:
    CHANNEL = each.name[8:11]
    DK = each.name[7]
    TIME = each.name[12:24]

    if DK == '1':
        mode = "full scan"
        filename = '%s.%s.FULL.png' % (TIME, CHANNEL)
    elif DK == '2':
        mode = "north heimsphere scan"
        filename = '%s.%s.NORTH.png' % (TIME, CHANNEL)
    else:
        mode = "south heimsphere scan"
        filename = '%s.%s.SOUTH.png' % (TIME, CHANNEL)
    print "> Start generation of image, channel %s, time %s, mode %s." % (CHANNEL, TIME, mode)

    print "> Extracting file..."
    try:
        sourceFile = tar.extractfile(each)
        source = sourceFile.read()
    except Exception,e:
        print e
        print "Error! Cannot extract this file. Skip."
        continue

    print "> Configuring plotter..."
    p = plotter()

    if 'VIS' == CHANNEL:
        visconv = """
        0:=-0.10
        1023:=100.00
        65535:=100.00
        """
        p.setColorScale(-10, 100)
        p.setConvertTable(visconv)
        p.setSourceRegion(59.995, 85.005, -60.005, -154.995)
        p.setDataDimension(12000, 12000)
        p.setDataResolution(0.01, 0.01)
    else:
        p.setColorScale(200, 300)
        p.setConvertTable(convert)
        p.setSourceRegion(59.98, 85.02, -60.02, -154.98)
        p.setDataDimension(3000, 3000)
        p.setDataResolution(0.04, 0.04)

    print "> Plotting data..."
    img = p.plotData(source)

    print "> Adding coastlines..."
    img = p.plotCoastlines(img)

    print "> Adding coordinate lines..."
    img = p.plotCoordinateLines(img)

    print "> Packing image..."
    img = p.packImage(img, timestamp=TIME, channel=CHANNEL)

    img.save(filename)
    print ">>> Image saved to: %s\n" % filename
