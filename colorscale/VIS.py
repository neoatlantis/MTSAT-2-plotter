#!/usr/bin/python

PALETTE = [] # color for labelings, coastlines, etc.
for i in xrange(0, 100):
    r = i * 2.55
    g = r
    b = r
    PALETTE.append(int(r))
    PALETTE.append(int(g))
    PALETTE.append(int(b))

##############################################################################

def getPaletteColor(x):
    if x > 100:
        x = 100 
    if x < 0:
        x = 0
    return int(x)
