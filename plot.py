#!/usr/bin/python

import math

##############################################################################

convert = """
0:=330.06
30:=327.69
60:=325.29
89:=322.92
117:=320.60
144:=318.32
171:=316.01
197:=313.74
222:=311.52
247:=309.26
271:=307.06
294:=304.91
317:=302.72
339:=300.59
360:=298.52
381:=296.41
401:=294.37
421:=292.29
440:=290.27
459:=288.22
477:=286.24
495:=284.22
512:=282.27
529:=280.28
545:=278.38
561:=276.44
576:=274.58
591:=272.68
605:=270.88
619:=269.04
632:=267.29
645:=265.51
658:=263.69
670:=261.98
682:=260.23
694:=258.44
705:=256.76
716:=255.05
727:=253.30
737:=251.68
747:=250.01
757:=248.31
766:=246.75
775:=245.15
784:=243.51
792:=242.02
800:=240.50
808:=238.94
816:=237.35
823:=235.92
830:=234.46
837:=232.97
844:=231.43
850:=230.09
856:=228.71
862:=227.31
868:=225.86
874:=224.38
879:=223.12
884:=221.83
889:=220.50
894:=219.15
899:=217.75
904:=216.32
908:=215.15
912:=213.95
916:=212.72
920:=211.46
924:=210.16
928:=208.83
932:=207.46
935:=206.41
938:=205.33
941:=204.23
944:=203.10
947:=201.93
950:=200.74
953:=199.51
956:=198.25
959:=196.95
962:=195.60
964:=194.68
966:=193.74
968:=192.77
970:=191.78
972:=190.76
974:=189.71
976:=188.64
978:=187.53
980:=186.39
982:=185.21
983:=184.61
984:=183.99
985:=183.37
986:=182.73
987:=182.08
988:=181.42
989:=180.75
990:=180.06
991:=179.35
992:=178.64
993:=177.90
994:=177.15
995:=176.38
996:=175.59
997:=174.78
998:=173.95
999:=173.10
1000:=172.22
1001:=171.32
1002:=170.38
1003:=169.42
1004:=168.42
1005:=167.39
1006:=166.32
1007:=165.20
1008:=164.04
1009:=162.83
1010:=161.55
1011:=160.21
1012:=158.80
1013:=157.30
1014:=155.70
1015:=153.99
1016:=152.14
1017:=150.12
1018:=147.90
1019:=145.43
1020:=142.60
1021:=139.30
1022:=135.27
1023:=129.99
65535:=129.99
"""
ir = 1
dk = 1
time = '201411172330'

source = open('testdata/%s.ir/IMG_DK0%dIR%d_%s.geoss' % (time, dk, ir, time), 'r').read()
##############################################################################

convertTable = [tuple(i.split(':=')) for i in convert.strip().split('\n')]
convertTable = [(int(i), float(j)) for i,j in convertTable]
convertTable = sorted(convertTable, key = lambda i:i[0])
def toTbb(x):
    global convertTable
    for i in xrange(0, len(convertTable)):
        if x >= convertTable[i][0]:
            break
    left, right = convertTable[i], convertTable[i+1]
    return 1.0 * (x - left[0]) / (right[0] - left[0]) * (right[1] - left[1])\
        + left[1]

##############################################################################

lngNW = 85.02
latNW = 59.98
latDelta = +0.04
lngDelta = +0.04
lngWidth = lngDelta * 3000
coeff = math.pi / 180.0
h = 3000 # draw picture height of h
r = h / 2 / math.tan(latNW * coeff)
w = int(r * coeff * lngWidth) + 1

def toPlotXY(lat, lng):
    global draw, r, w, h, latDelta, lngDelta, lngNW, latNW, drawW_2, coeff
    rLatTan = r * math.tan(lat * coeff)
    if lng < 0:
        lng += 360
    lngDiff = lng - lngNW
    drawX = r * (lngDiff * coeff)  + 0
    drawY = h / 2 - rLatTan        + 0
    return drawX, drawY
       
##############################################################################
# Prepare for image drawing

from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont

#img = Image.new('L', (w, h), 'white')
imgbuffer = [255,] * (w + 1) * (h + 1)
#draw = ImageDraw.Draw(img)

drawW_2  = r * (latDelta / 2.0 * coeff)
def plot(x, y, value):
    global draw, r, w, h, latDelta, lngDelta, lngNW, latNW, drawW_2, coeff, imgbuffer
    lat = latNW - y * latDelta
    lng = lngNW + x * lngDelta
    drawX1, drawY1 = toPlotXY(lat + latDelta / 2.0, lng - latDelta / 2.0)
    drawX2, drawY2 = toPlotXY(lat - latDelta / 2.0, lng + lngDelta / 2.0)

    color = int((value - 100) / (340 - 100) * 255.0)
#    draw.rectangle([(drawX1, drawY1), (drawX2, drawY2)], fill=color)

    rectY = int(abs(drawY2 - drawY1)) + 1
    rectX = int(abs(drawX2 - drawX1)) + 1
    offset = int(drawY1) * w + int(drawX1)
    if offset < 0:
        return
#    print drawY1, drawX1, rectY,rectX, offset
#    exit()
    for i in xrange(0, rectY):
        for j in xrange(0, rectX):
            imgbuffer[offset + j] = color
        offset += w
            

##############################################################################
# draw image

index = 0
Tbb = 0

i = 0
for y in xrange(0, 3000):
    for x in xrange(0, 3000):
        Tbb = toTbb((ord(source[index]) << 8) + ord(source[index+1]))
        plot(x, y, Tbb)
        index += 2
        i += 1
    if y % 30 == 0:
        print str(y / 30.0) + '%'

#print imgbuffer[:30]

imgbuffer = ''.join([chr(i) for i in imgbuffer])
img = Image.frombytes('L', (w, h), imgbuffer)

##############################################################################
# grey image adjust
img = ImageOps.invert(img)

img = ImageOps.equalize(img)

# enhance constrast
contrastEnhancer = ImageEnhance.Contrast(img)
contrastEnhancer.enhance(10)

"""
# brightness enhancer
brightnessEnhancer = ImageEnhance.Brightness(img)
brightnessEnhancer.enhance(0.5)
"""

##############################################################################

imgColor = Image.merge('RGB', (img, img, img))
drawColor = ImageDraw.Draw(imgColor)

def lineColor(lat1, lng1, lat2, lng2, rgb, bold):
    drawX1, drawY1 = toPlotXY(lat1, lng1)
    drawX2, drawY2 = toPlotXY(lat2, lng2)
    drawColor.line([(drawX1, drawY1), (drawX2, drawY2)], fill="rgb(%d,%d,%d)" % rgb, width=bold)
def drawText(lat, lng, offsetX, offsetY, text, font):
    drawX, drawY = toPlotXY(lat, lng)
    drawColor.text((drawX + offsetX, drawY + offsetY), str(text), font=font, fill="red")
    

# draw coastline

import shapefile
coastline = shapefile.Reader('coastline/ne_10m_coastline')
for each in coastline.shapes():
    points = each.points
    useLine = False
    for lng, lat in points:
        if latNW < abs(lat):
            continue
        if lng >= 0:
            if lng < lngNW:
                continue
        else:
            if lng + 360 > lngNW + 180:
                continue
        useLine = True
    if useLine:
        start = False
        lastLng, lastLat = 0, 0
        curLng, curLat = 0, 0
        for lng, lat in points:
            curLng, curLat = lng, lat
            if start:
                lineColor(lastLat, lastLng, curLat, curLng, (255, 0, 255), 1)
            else:
                start = True
            lastLng, lastLat = curLng, curLat


# draw grid lines

font = ImageFont.truetype('font.ttf', 32)

for lat in xrange(-60, 61, 15):
    lineColor(lat, lngNW, lat, lngNW + 130, (255,0,0), 2)
    if lat > 0:
        strlat = str(lat) + 'N'
    elif lat < 0:
        strlat = str(-lat) + 'S'
    else:
        strlat = 'EQUATOR'
    textW, textH = font.getsize(strlat)
    drawText(lat, lngNW, 2, -textH-5, strlat, font)

for lng in xrange(60, 300, 15):
    lineColor(-70, lng, 70, lng, (255, 0, 0), 2)
    if lng > 180:
        strlng = str(360 - lng) + 'W'
    else:
        strlng = str(lng) + 'E'
    textW, textH = font.getsize(strlng)
    drawText(0, lng, -textW-2, 2, strlng, font)

##############################################################################

margin = 20
imgEnv = Image.new('RGB', (w + 700 + 2 * margin, h + 2 * margin), 'rgb(100,100,100)')
imgCrop = imgColor.crop((0, 0, w, h))

imgEnv.paste(imgCrop, (margin, margin, margin + w, margin + h))

envDraw = ImageDraw.Draw(imgEnv)
envT = margin
envL = w + margin * 2
textH = font.getsize('X')[1]
def envLabel(text):
    global envDraw, envH, envT, textH
    envDraw.text((envL, envT), text, font=font, fill="black")
    envT += textH * 1.5

text = ("""
NeoAtlantis MTSAT-2 IR Data Plotter
===================================

Data Time: %s
IR: %d






This program is free software: you
can redistribute it and/or modify
it under the terms of the GNU
General Public License as published
by the Free Software Foundation,
either version 3 of the License, or
(at your option) any later version.

This program is distributed in the
hope that it will be useful, but
WITHOUT ANY WARRANTY; without even
the implied warranty of 
MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU
General Public License for more
details.

You should have received a copy of
the GNU General Public License
along with this program.  If not,
see <http://www.gnu.org/licenses/>.
""" % (time, ir)).strip().split('\n')
for line in text:
    envLabel(line.strip())

imgEnv.save('output.png')
