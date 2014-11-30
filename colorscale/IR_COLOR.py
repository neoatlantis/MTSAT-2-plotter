#!/usr/bin/python

PALETTE = [255, 100, 0] # color for labelings, coastlines, etc.
for i in xrange(-90, 30, 2):
    r,g,b = 0, 0, 0
    if i <= -80:
        r = 255
        g = 127 + (i + 90) * 12.7
    elif i <= -70:
        r = 127 + (i + 80) * 12.7
    elif i <= -50:
        g = 155 + (i + 70) * 5
    elif i <= -30:
        b = 255
        g = (i + 50) * 12.75
    elif i <= 30:
        r = 255 - (i + 30) * 4.25
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
    index = int((celsius + 90.0) / 2) + 1
    return index
