#!/usr/bin/python

import os
from subprocess import *
import sys

from PIL import Image


def convert(table, dimension, dataString):
    tableStr = ''.join([chr(i) for i in table])
    
    print "Calling C converter..."
    proc = Popen(['./converter'], stdin=PIPE, stdout=PIPE, shell=True, bufsize=0)
    strout, strerr = proc.communicate(tableStr + dataString)
    print "C converter called..."

    endstr = strout[-2:]
    strout = strout[:-2]

    return strout
