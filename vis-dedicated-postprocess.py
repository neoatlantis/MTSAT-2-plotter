#!/usr/bin/python

import sys
import os

if len(sys.argv) < 2:
    print "Usage: python vis-dedicated-postprocess.py <FILENAME>"
    exit()


PATH = sys.argv[1]
FILENAME = os.path.basename(PATH)


