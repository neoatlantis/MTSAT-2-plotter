#!/usr/bin/env python

import os
import sys
import re
import subprocess
from pipes import quote

from calibtable import getCalibrationTable
from convfunc import getConversionFunction

##############################################################################

# Determine input and output file paths

if len(sys.argv) < 2:
    print "Usage: python raw2pgm.py <INPUT FILE>"
    sys.exit(1)

inputFile = sys.argv[1]
inputFilepath = os.path.realpath(os.path.dirname(inputFile))
inputFilename = os.path.basename(inputFile)
inputFile = os.path.join(inputFilepath, inputFilename)

rs = re.match(
    '^([0-9]{12})\.(vis|ext|sir|tir)\.([0-9]{2})\.fld\.geoss(\.bz2){0,1}$',
    inputFilename)
if not rs:
    print "Input seems not being a valid compressed geoss data tarball."
    sys.exit(2)

timestamp = rs.group(1)
bandName = rs.group(2)
bandNumber = int(rs.group(3))
fileSuffix = rs.group(4)

outputPgmpath = os.path.join(
    inputFilepath, 
    "%s.%s.%02d.pgm" % (timestamp, bandName, bandNumber))

decompressData = os.path.join(
    inputFilepath,
    "%s.%s.%02d.fld.geoss" % (timestamp, bandName, bandNumber))

convtableFile = os.path.join(
    inputFilepath,
    "%s.%s.%02d.conv" % (timestamp, bandName, bandNumber))

##############################################################################

# Decompress geoss file

if fileSuffix == '.bz2':
    print "Decompress file %s" % inputFilename
    subprocess.call(['bunzip2', '-f', inputFile])

if not os.path.getsize(decompressData) in [72000000, 288000000, 1152000000]:
    print "Unexpected raw data size. Break."
    sys.exit(3)

##############################################################################

# Get calibration table (counts->physical value)

print "Generating calibration table"
ctable = getCalibrationTable(bandName, bandNumber)

##############################################################################

# Get conversion table (physical value->greyscale)

print "Generating conversion table"
cfunc = getConversionFunction(bandName, bandNumber)
ctable = [chr(cfunc(i)) for i in ctable]
assert len(ctable) == 65536

##############################################################################

# Decide picture size

pictureSize = {
    'ext': 24000,
    'vis': 12000,
    'sir': 6000,
    'tir': 6000,
}[bandName]

# Call converter

f1 = open(convtableFile, 'w+')
f1.write(''.join(ctable))
f1.close()

print "Writing PGM file header"

f1 = open(outputPgmpath, 'w+')
f1.write("P5\n# NeoAtlantis\n%d %d\n255\n" %(
    pictureSize,
    pictureSize
))
f1.close()

print "Conversion and write data to PGM"

subprocess.call("cat %s %s | ./converter >> %s" % (
    quote(convtableFile), 
    quote(decompressData),
    quote(outputPgmpath)
), shell=True)

print "Delete intermediate files"
os.unlink(convtableFile)
