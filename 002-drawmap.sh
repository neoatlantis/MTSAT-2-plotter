#!/bin/bash

# generate index
ls -1 site/data > site/data/index.txt

echo "Clearing tasks..."

# call task generator to generate tasks
python task.py

# generate index
ls -1 site/data > site/data/index.txt
