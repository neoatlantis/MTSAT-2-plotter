#!/usr/bin/env python

import argparse
import os
import sys
import re
import subprocess
from pipes import quote

from calibtable import getCalibrationTable
from convfunc import getConversionFunction

##############################################################################

parser = argparse.ArgumentParser(\
    description="""
    A multi-purpose tool for downloading and generating high-resolution
    satellite images from Himawari-8. You need to ensure `wget`, `bunzip2` and
    `cat` commands are available on this system. And you have to first use gcc
    to compile the C converter: `gcc converter.c -o converter`
    """
)

parser.add_argument(
    'command',
    choices=['list', 'download', 'draw'],
    help="""What would you like to do with this tool. For `list`, the program
    will connect to the FTP server located at <hmwr829gr.cr.chiba-u.ac.jp> and
    list available tarballs for downloading. For `download` with given argument
    on timestamp and channel, a tarball will be downloaded. For `draw`, specify
    a downloaded tarball, this tool will generate a PGM grey scale picture
    using its data.
    """
)

parser.add_argument(
    '--date',
    action='store',
    type=str,
    required=False,
    help="""Required and valid only when `list` is choosen. Otherwise ignored.
    Give this option with a 6-digits value like 201606, to specify a month
    from which all available tarballs will be listed. The date is UTC.
    """
)

parser.add_argument(
    '--timestamp',
    action='store',
    type=str,
    required=False,
    help="""Required when `download` is choosen. Specify a timestamp of the
    data being transmitted. The timestamp must consist 12 digits in format of
    YYYYmmDDHHMM, e.g. a 4-digits year, a 2-digits month, a 2-digits day, and
    hour as well as minute in 2-digits each. Example: 201606010230. The
    timestamp is UTC.
    """
)

parser.add_argument(
    '--channel',
    action='store',
    choices=[
        'ext', 'vis', 'sir', 'tir',
        'ext01', 'vis01', 'vis02', 'vis03', 'sir01', 'sir02', 'tir01', 'tir02',
        'tir03', 'tir04', 'tir05', 'tir06', 'tir07', 'tir08', 'tir09', 'tir10',
    ],
    required=False,
    help="""
        Required when `download` or `list` is choosen.  Choose a channel. To
        `list`, just one choice out of `ext`, `vis`, `sir`, `tir` is enough. To
        `download`, you must also specify the channel ID, e.g. 01-10 depending
        on channel choice.
    """
)

parser.add_argument(
    '--input',
    action='store',
    required=False,
    help="""Required when `draw` is choosen. Give the input file name. Can be
    either a `.geoss`(decompressed) or `.geoss.bz2`(compressed) file.
    """
)

args = parser.parse_args()

COMMAND = args.command

DATE = args.date
if 'list' == COMMAND:
    try:
        assert re.match('^[0-9]{4}(0[1-9]|10|11|12)$', DATE)
    except:
        print "Which month would you like to be listed? Use `--date YYYYMM`."
        sys.exit(1)

TIMESTAMP = args.timestamp
if 'download' == COMMAND:
    try:
        assert re.match('^[0-9]{12}$', TIMESTAMP)
    except:
        print "From which time should the data originate? Use `--timestamp YYYYmmDDHHMM`."
        sys.exit(1)

CHANNELNAME, CHANNELID = '', -1 
if args.channel:
    CHANNELNAME = args.channel[:3].upper()
    CHANNELID = int(args.channel[3:] or -1)
    if COMMAND == 'download' and CHANNELID == -1:
        print "You must specify the full channel representation, e.g. XXXYY"
        sys.exit(1)
elif COMMAND in ['download', 'list']:
    print "You must specify the channel. Use --channel argument."
    sys.exit(1)

inputFile = args.input

##############################################################################

# If used for listing or downloading

if 'list' == COMMAND:
    from ftplist import listHMWR8
    listHMWR8(DATE, CHANNELNAME)
    sys.exit()

if 'download' == COMMAND:
    filename = '%s.%s.%02d.fld.geoss.bz2' % (
        TIMESTAMP, CHANNELNAME.lower(), CHANNELID, 
    )
    url = 'ftp://hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20151105/%s/%s/%s' % (\
        TIMESTAMP[:6], CHANNELNAME, filename
    )
    subprocess.call(['wget', url])
    sys.exit()

##############################################################################

# Determine input and output file paths

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
