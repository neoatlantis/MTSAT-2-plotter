#!/bin/bash

# get date marker, e.g. 201411
_DATEMONTH=`date +%Y%m`

echo "Clearing tasks for month $_DATEMONTH ..."

# call task generator to generate tasks
python task.py $_DATEMONTH 

# clean cache file
rm -f cache.pgm
