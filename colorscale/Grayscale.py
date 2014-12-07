#!/usr/bin/python

PALETTE = [] # color for labelings, coastlines, etc.
for i in xrange(0, 241):
    PALETTE += [i] * 3

"""for i in xrange(-90, 31, 1):
    r = (i + 90) * 2
    g = r
    b = r
    PALETTE.append(int(r))
    PALETTE.append(int(g))
    PALETTE.append(int(b))
"""

##############################################################################

def getPaletteColor(Tbb):
    celsius = Tbb - 273.15
    index = int(round((celsius + 90.0) * 2))
    if index > 240:
        index = 240
    if index < 0:
        index = 0
    return index
