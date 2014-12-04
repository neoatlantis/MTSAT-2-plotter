#!/usr/bin/python

PALETTE = [] # color for labelings, coastlines, etc.
for i in xrange(-90, 31, 2):
    r = (i + 90) * 2
    g = r
    b = r
    PALETTE.append(int(r))
    PALETTE.append(int(g))
    PALETTE.append(int(b))

##############################################################################

def getPaletteColor(Tbb):
    celsius = Tbb - 273.15
    if celsius > 30:
        celsius = 30.0
    if celsius < -90:
        celsius = -90.0
    index = int((celsius + 90.0) / 2)
    return index
