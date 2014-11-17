#!/usr/bin/python

import math

##############################################################################

convert = """
0:=300.03
36:=298.52
71:=297.02
105:=295.52
138:=294.03
170:=292.54
201:=291.06
230:=289.64
259:=288.18
287:=286.73
314:=285.30
340:=283.88
365:=282.48
389:=281.09
412:=279.73
435:=278.32
457:=276.94
478:=275.59
498:=274.26
518:=272.90
537:=271.56
555:=270.26
573:=268.92
590:=267.62
606:=266.36
622:=265.07
637:=263.81
652:=262.52
666:=261.29
680:=260.01
693:=258.79
706:=257.53
718:=256.33
730:=255.10
741:=253.94
752:=252.74
763:=251.50
773:=250.34
783:=249.15
792:=248.04
801:=246.89
810:=245.71
818:=244.63
826:=243.52
834:=242.37
842:=241.18
849:=240.11
856:=239.00
863:=237.86
869:=236.85
875:=235.81
881:=234.73
887:=233.62
892:=232.66
897:=231.68
902:=230.66
907:=229.61
912:=228.53
917:=227.40
921:=226.47
925:=225.51
929:=224.52
933:=223.50
937:=222.43
940:=221.61
943:=220.77
946:=219.90
949:=219.00
952:=218.07
955:=217.11
958:=216.12
961:=215.09
964:=214.01
966:=213.27
968:=212.51
970:=211.73
972:=210.93
974:=210.09
976:=209.23
978:=208.35
980:=207.42
982:=206.47
983:=205.97
984:=205.47
985:=204.96
986:=204.43
987:=203.90
988:=203.35
989:=202.79
990:=202.22
991:=201.63
992:=201.02
993:=200.40
994:=199.77
995:=199.11
996:=198.44
997:=197.75
998:=197.03
999:=196.29
1000:=195.53
1001:=194.73
1002:=193.91
1003:=193.06
1004:=192.17
1005:=191.24
1006:=190.26
1007:=189.24
1008:=188.17
1009:=187.03
1010:=185.83
1011:=184.55
1012:=183.18
1013:=181.70
1014:=180.09
1015:=178.33
1016:=176.38
1017:=174.18
1018:=171.66
1019:=168.69
1020:=165.02
1021:=160.17
1022:=152.70
1023:=129.99
65535:=129.99
"""
source = open('testdata/201411171530.ir/IMG_DK01IR1_201411171530.geoss', 'r').read()


##############################################################################

convertTable = [tuple(i.split(':=')) for i in convert.strip().split('\n')]
convertTable = [(int(i), float(j)) for i,j in convertTable]
convertTable = sorted(convertTable, key = lambda i:i[0])
def toTbb(x):
    global convertTable
    for i in xrange(0, len(convertTable)):
        if x > convertTable[i][0]:
            break
    left, right = convertTable[i], convertTable[i+1]
    return 1.0 * (x - left[0]) / (right[0] - left[0]) * (right[1] - left[1])\
        + left[1]

##############################################################################

lngNW = 85.02
latNW = 59.98
latDelta = +0.04
lngDelta = +0.04
coeff = math.pi / 180.0
       
##############################################################################
# Prepare for image drawing

from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont

w = 2000
h = 3000
img = Image.new('L', (w, h), 'white')
draw = ImageDraw.Draw(img)

r = h / 2 / math.tan(latNW * coeff)
drawW_2  = r * (latDelta / 2.0 * coeff)
def plot(x, y, value):
    global draw, r, w, h, latDelta, lngDelta, lngNW, latNW, drawW_2, coeff
    lat = (latNW - y * latDelta) * coeff
    rLatTan = r * math.tan(lat)
    drawX = r * (x * lngDelta * coeff)
    drawY = h / 2 - rLatTan 
    drawH_p = r * math.tan(lat + latDelta * coeff) - rLatTan 
    drawH_n = rLatTan - r * math.tan(lat - latDelta * coeff)
    color = (value - 100) / (340 - 100) * 255.0
    draw.rectangle([(drawX - drawW_2, drawY - drawH_p), (drawX + drawW_2, drawY + drawH_n)], fill=color)

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

def pointColor(latDeg, lngDeg, rgb, bold=2):
    global drawColor, r, w, h, latDelta, lngDelta, lngNW, latNW, coeff
    lat = latDeg * coeff
    if lngDeg < 0:
        lngDeg += 360
    lngDiff = lngDeg - lngNW
    drawX = r * (lngDiff * coeff)
    drawY = h / 2 - r * math.tan(lat)
    drawColor.rectangle([(drawX - bold / 2.0, drawY - bold / 2.0), (drawX + bold / 2.0, drawY + bold / 2.0)], fill="rgb(%d,%d,%d)" % rgb)
    return drawX, drawY

font = ImageFont.truetype('font.ttf', 32)
fontW, fontH = font.getsize('X')

lastX, lastY = 0, 0
for lat in xrange(-60, 61, 15):
    for lng in xrange(int(lngNW), int(lngNW) + 130):
        for x in xrange(0, 10):
            lastX, lastY = pointColor(lat, lng + x / 10.0, (255,0,0))
    drawColor.text((lastX - fontW * 3, lastY - fontH * 1.6), str(lat), font=font, fill="red")

for lng in xrange(60, 300, 15):
    for lat in xrange(-70, 70):
        for y in xrange(0, 10):
            lastX, lastY = pointColor(lat + y / 10.0, lng , (255,0,0))
    if lng > 180:
        strlng = str(lng - 360)
    else:
        strlng = str(lng)
    drawColor.text((lastX - fontW * 3, fontH * 1.6), strlng, font=font, fill="red")

imgColor.save('output.png')
