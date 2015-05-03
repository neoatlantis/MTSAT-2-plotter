#!/usr/bin/python
import math

def hsvToRgb(h, s, v):
    i = math.floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    x = i % 6
    if 0 == x:
        r,g,b = v,t,p
    elif 1 == x:
        r,g,b = q,v,p
    elif 2 == x:
        r,g,b = p,v,t
    elif 3 == x:
        r,g,b = p,q,v
    elif 4 == x:
        r,g,b = t,p,v
    elif 5 == x:
        r,g,b = v,p,q

    return (r * 255, g * 255, b * 255)


PALETTE = [255, 100, 0] # color for labelings, coastlines, etc.
i = -90.0
while i <= 30.0:
    r,g,b = 0, 0, 0
    h,s,v = 0, 100, 100

    if i < -80:
        h = 36 + 2.4 * (i + 90)
        s = 85 + 1.5 * (i + 90)
    elif i <= -70:
        h = 30 - 3 * (i + 80)
        s = 75 + 2.5 * (i + 80)
        v = 60 + 4 * (i + 80)
    elif i < -50:
        h = 120 - 1.5 * (i + 70)
        s = 100
        v = 60 + 2 * (i + 70)
    elif i < -30:
        h = 240 - 2.5 * (i + 50)
        s = 100
        v = 70 + 1.5 * (i + 50)
    elif i < 30:
        h = 0
        s = 0
        v = 100 - 100 * (i + 30) / 60
    else: 
        h = 0; s = 0; v = 0;

    h /= 360
    s /= 100
    v /= 100

    r,g,b = hsvToRgb(h, s, v)

    PALETTE.append(int(r))
    PALETTE.append(int(g))
    PALETTE.append(int(b))

    i += 0.5

##############################################################################

def getPaletteColor(Tbb):
    celsius = Tbb - 273.15
    if celsius > 30:
        celsius = 30.0
    if celsius < -90:
        celsius = -90.0
    index = int((celsius + 90.0) * 2) + 1
    return index
