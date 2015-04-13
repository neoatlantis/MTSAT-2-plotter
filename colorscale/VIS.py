#!/usr/bin/python

PALETTE = [255, 0, 0] # color for labelings, coastlines, etc.
for i in xrange(0, 250):
    r = i / 250.0 * 256.0
    g = r
    b = r
    PALETTE.append(int(r))
    PALETTE.append(int(g))
    PALETTE.append(int(b))

##############################################################################

def getPaletteColor(x):
    if x > 100:
        x = 100.0 
    if x < 0:
        x = 0.0
    x *= 2.5
    return 1 + int(x)
