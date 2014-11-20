#!/bin/bash

# get date marker, e.g. 201411
_DATEMONTH=`date +%Y%m`

echo "Sync MTSAT-2 IR data for month $_DATEMONTH ..."

# create mirror/<date> and result/<date> for storing data
mkdir -p mirror/$_DATEMONTH result/$_DATEMONTH

# call the `ftpcopy` command to synchronize the files
#   --dry-run       for testing purposes
#   --max-days 1    for limiting the old date
#   -l 2            log level 2
#   -x "*vis*"      excluding VISUAL data
./ftpcopy --dry-run --max-days 1 -l 2 -x "*vis*" ftp://mtsat-1r.cr.chiba-u.ac.jp/grid-MTSAT-2.0/MTSAT2/$_DATEMONTH/ mirror/$_DATEMONTH
