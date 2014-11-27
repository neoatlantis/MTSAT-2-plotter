#!/usr/bin/python

import os
from subprocess import *
import sys


def convert(table, dataString):
    tableStr = ''.join([chr(i) for i in table])
    
    print "Calling C converter..."
    proc = Popen(['./converter'], stdin=PIPE, stdout=PIPE, shell=True, bufsize=0)
    strout, strerr = proc.communicate(tableStr + dataString)
    print "C converter called..."
    
    return strout
