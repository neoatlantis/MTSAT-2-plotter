#!/bin/bash

# get date marker, e.g. 201411
_DATEMONTH=`date +%Y%m`

echo "Sync MTSAT-2 IR data for month $_DATEMONTH ..."

# delete mirror and result files that are too old
echo "Removing files that are old..."
find ./mirror -type f -mtime +2 -exec rm -rf {} \;
find ./result -type f -mtime +7 -exec rm -rf {} \;

# create mirror/<date> and result/<date> for storing data
mkdir -p mirror/$_DATEMONTH result/$_DATEMONTH

# call the `ftpcopy` command to synchronize the files
#   --dry-run       for testing purposes
#   --max-days 1    for limiting the old date
#   -l 2            log level 2
#   -x "*vis*"      excluding VISUAL data
./ftpcopy --max-days 1 -l 2 -x "*vis*" ftp://mtsat-1r.cr.chiba-u.ac.jp/grid-MTSAT-2.0/MTSAT2/$_DATEMONTH/ mirror/$_DATEMONTH

# call task generator to generate tasks
python task.py $_DATEMONTH
