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

    print "Write PGM file"
    open('cache.pgm', 'w+').write(('P5\n#\n%d %d\n255\n' % dimension) + strout)
    print 'PGM file wrote'
    
    return (ord(endstr[0]), ord(endstr[1])), Image.open('cache.pgm')
