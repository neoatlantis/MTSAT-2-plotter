#!/bin/bash

# get date marker, e.g. 201411
_DATEMONTH=`date -u +%Y%m`

echo "Clearing tasks for month $_DATEMONTH ..."

# call task generator to generate tasks
python task.py $_DATEMONTH 

# generate index
ls -1 site/data > site/data/index.txt
