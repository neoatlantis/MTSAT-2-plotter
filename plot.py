#!/usr/bin/python
"""
NeoAtlantis MTSAT-2 Data Plotter
Copyright (C) 2014 NeoAtlantis 

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import array
import math
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont

#from plotconfig import drawData, drawCoastline, projectionMethod, markRegion
#from plotconfig import cropLatN, cropLatS, cropLngDiffW, cropLngDiffE
import shapefile
##############################################################################

class plotter:

    coeff = math.pi / 180.0
    projectionMethod = 'equirectangular'
    
    def __init__(self):
        pass

    def setConvertTable(self, convert):
        # Cache the tablized curve. A look up table from Uint16 to Color
        # Value(0-255) is calculated and cached.
        convert = convert.strip().split('\n')
        curve = [tuple(i.strip().split(':=')) for i in convert]
        curve = [(int(i), float(j)) for i,j in curve]
        curve = sorted(curve, key = lambda i:i[0])

        # get curve Y range
        curveYMax = -99999
        curveYMin = 99999
        for x,y in curve:
            if y > curveYMax:
                curveYMax = y
            if y < curveYMin:
                curveYMin = y
        self.colorScaleRange = curveYMin, curveYMax

        tableSize = 65536 # TODO use the size from curve
        self.lookupTable = [0,] * tableSize

        curveLen = len(curve)
        for x in xrange(0, tableSize):
            for i in xrange(0, curveLen):
                if x >= curve[i][0] and x <= curve[i+1][0]:
                    break
            left, right = curve[i], curve[i+1]
            value = 1.0 * (x - left[0]) / (right[0] - left[0])
            value *= (right[1] - left[1])
            value += left[1]
            self.lookupTable[x] = self.__getGreyScale(value)

    def setSourceRegion(self, srcLatN, srcLngW, srcLatS, srcLngE):
        self.sourceRegion = (srcLatN, srcLngW, srcLatS, srcLngE)
        if srcLngW < srcLngE:
            self.sourceRegionSize = (srcLatN-srcLatS, srcLngE-srcLngW)
        else:
            self.sourceRegionSize = (srcLatN-srcLatS, 360-srcLngW+srcLngE)

    def setDataDimension(self, w, h):
        self.dataDimension = (w, h)

    def setDK(self, dk):
        self.dk = dk
        w, h = self.dataDimension
        if dk == '1':
            self.effectiveRegion = (0, 0, w, h)
        elif dk == '2':
            self.effectiveRegion = (0, 0, w, h / 2)
        else:
            self.effectiveRegion = (0, h/2, w, h)

    def setDataResolution(self, latRes, lngRes):
        self.dataResolution = (latRes, lngRes) # deltaLat, deltaLng

    def setScaleParameters(self, inverted, unit):
        self.colorScaleInverted = inverted
        self.colorScaleUnit = unit

    def _getPaintColor(self, uint16):
        # Convert the satellite result, which is Uint16, into Uint8 grey scale
        # color. This is done by simply looking up the lookup table
        # precalculated.
        return self.lookupTable[uint16]

    def __getGreyScale(self, value):
        inverted = self.colorScaleInverted
        minimal, maximal = self.colorScaleRange
        if inverted:
            color = 255 - int((value - minimal) / (maximal - minimal) * 255.0)
        else:
            color = int((value - minimal) / (maximal - minimal) * 255.0)
        if color > 255:
            color = 255
        elif color < 0:
            color = 0
        return color

    def __getPhysicalValue(self, greyScale):
        inverted = self.colorScaleInverted
        minimal, maximal = self.colorScaleRange
        if inverted:
            value = (1 - greyScale / 255.0) * (maximal - minimal) + minimal
        else:
            value = (greyScale / 255.0) * (maximal - minimal) + minimal
        return value

    def __project(self, lat, lng):
        if lng < 0:
            lng += 360
        lngDiff = lng - self.sourceRegion[1] # lng - srcLngW
        drawX = lngDiff / self.dataResolution[1]
        drawY = self.dataDimension[1] / 2 - lat / self.dataResolution[0]
        return int(drawX), int(drawY)

    def plotData(self, dataString):
        # plot data
        #   dataDimension := (X-points, Y-points), given by MTSAT-2
        dataColorMatrix = array.array('B')
        dataSize = self.dataDimension[0] * self.dataDimension[1]
        if dataSize != len(dataString) / 2:
            raise Exception('Wrong data dimension specification.')

        ri = 0
        maxGrey, minGrey = -99999, 99999
        for percent in xrange(0, 100):
            for i in xrange(0, dataSize / 100):
                uint16 = (ord(dataString[ri]) << 8) + ord(dataString[ri+1])
                greyScale = self._getPaintColor(uint16)
                dataColorMatrix.append(greyScale)
                if greyScale > maxGrey:
                    maxGrey = greyScale 
                if greyScale < minGrey:
                    minGrey = greyScale 
                ri += 2
            print "%d %%" % percent
        
        # maxGrey and minGrey are color grey extreme scales that are actually
        # drawn on the map.

        maxPhysicalValue = self.__getPhysicalValue(maxGrey)
        minPhysicalValue = self.__getPhysicalValue(minGrey)

        # form the data map

        imgGrey = Image.frombuffer('L', self.dataDimension, dataColorMatrix, 'raw', 'L', 0, 1)

        imgCrop = imgGrey.crop(self.effectiveRegion)
        imgCrop = ImageOps.equalize(imgCrop)
        imgGrey.paste(imgCrop, self.effectiveRegion)

        imgColor = Image.merge('RGB', (imgGrey, imgGrey, imgGrey))

        # imgColor, imgColorScaleInfo(minPhy, maxPhy)
        return imgColor, (minPhysicalValue, maxPhysicalValue)

    def _lineColor(self, imgDraw, lat1, lng1, lat2, lng2, color, bold):
        drawX1, drawY1 = self.__project(lat1, lng1)
        drawX2, drawY2 = self.__project(lat2, lng2)
        imgDraw.line([(drawX1, drawY1), (drawX2, drawY2)], fill=color, width=bold)

    def _drawText(self, imgDraw, lat, lng, offsetX, offsetY, text, font, color):
        drawX, drawY = self.__project(lat, lng)
        imgDraw.text((drawX + offsetX, drawY + offsetY), str(text), font=font, fill=color)

    def _drawCross(self, lat, lng, size, color):
        global drawColor
        drawX, drawY = toPlotXY(lat, lng)
        size = size / 2
        drawColor.line([(drawX - size, drawY), (drawX + size, drawY)], fill="rgb(%d,%d,%d)" % color, width = 2)
        drawColor.line([(drawX, drawY - size), (drawX, drawY + size)], fill="rgb(%d,%d,%d)" % color, width = 2)

    def plotCoastlines(self, imgColor):
        imgR, imgG, imgB = imgColor.split()
        imgDraw = ImageDraw.Draw(imgG)
        latN, lngW, latS, lngE = self.sourceRegion
        coastline = shapefile.Reader('coastline/ne_50m_coastline')
        for each in coastline.shapes():
            points = each.points
            if len(points) < 2:
                continue
            lastLng, lastLat = points[0]
            for lng, lat in points[1:]:
                self._lineColor(imgDraw, lastLat, lastLng, lat, lng, 255, 2)
                lastLng, lastLat = lng, lat
        img = Image.merge('RGB', (imgR, imgG, imgB))
        return img

    def plotCoordinateLines(self, imgColor):
        imgR, imgG, imgB = imgColor.split()
        imgDraw = ImageDraw.Draw(imgR)
        font = ImageFont.truetype('font.ttf', 32)
        
        latN, lngW, latS, lngE = self.sourceRegion
        latHeight, lngWidth = self.sourceRegionSize

        for lat in xrange(-60, 61, 15):
            self._lineColor(imgDraw, lat, lngW, lat, lngW + lngWidth, 255, 3)
            if lat > 0:
                strlat = str(lat) + 'N'
            elif lat < 0:
                strlat = str(-lat) + 'S'
            else:
                strlat = 'EQUATOR'
            textW, textH = font.getsize(strlat)
            self._drawText(imgDraw, lat, lngW, 2, -textH-5, strlat, font, 255)

        for lng in xrange(60, 300, 15):
            self._lineColor(imgDraw, latS, lng, latN, lng, 255, 3)
            if lng > 180:
                strlng = str(360 - lng) + 'W'
            else:
                strlng = str(lng) + 'E'
            textW, textH = font.getsize(strlng)
            self._drawText(imgDraw, 0, lng, -textW-2, 2, strlng, font, 255)
        
        img = Image.merge('RGB', (imgR, imgG, imgB))
        return img

        """
        # mark out regions
        for each in markRegion:
            region = each["region"]
            center = each["center"]
            p1, p2 = region[:2]
            p1Lat, p1Lng = p1
            p2Lat, p2Lng = p2
            centerLat, centerLng = (p1Lat + p2Lat) / 2.0, (p1Lng + p2Lng) / 2.0 
            
            lineColor(imgDraw, p1Lat, p1Lng, p2Lat, p1Lng, (0, 0, 255), 2)
            lineColor(imgDraw, p2Lat, p1Lng, p2Lat, p2Lng, (0, 0, 255), 2)
            lineColor(p2Lat, p2Lng, p1Lat, p2Lng, (0, 0, 255), 2)
            lineColor(p1Lat, p2Lng, p1Lat, p1Lng, (0, 0, 255), 2)

            if center:
                drawCross(centerLat, centerLng, 16, (0,0,255))
        """

    def packImage(self, img, **argv):
        font = ImageFont.truetype('font.ttf', 32)
        margin = 20
        w, h = img.size
        imgEnvSize = (w + 700 + 2 * margin, h + 2 * margin)
        imgEnv = Image.new('RGB', imgEnvSize, 'rgb(100,100,255)')
        imgCrop = img.crop((0, 0, w, h))
        envDraw = ImageDraw.Draw(imgEnv)

        imgDataRegion = (margin, margin, margin + w, margin + h)
        imgEnv.paste(imgCrop, imgDataRegion)

        envT = margin
        envL = w + margin * 2
        textW, textH = font.getsize('X')

        time = argv["timestamp"]
        timestamp = time[0:4] + '-' + time[4:6] + '-' + time[6:8] + ' '
        timestamp += time[8:10] + ':' + time[10:12] + ' '
        timestamp += 'UTC'

        if self.dk == '1':
            dataRegionDesc = "N+S Hemisphere"
        elif self.dk == '2':
            dataRegionDesc = "N Hemisphere"
        else:
            dataRegionDesc = "S Hemisphere"

        text = """
        NeoAtlantis MTSAT-2 Data Plotter
        ===================================

        Timestamp: %s
        Channel: %s
        Data Region: %s

        MTSAT gridded data are provided by
        the Center for Environmental Remote 
        Sensing, Chiba University and 
        sponsored by the ``Formation of a 
        virtual laboratory for diagnosing 
        the earth's climate system'' the
        Ministry of Science, Sports, and
        Culture. Original image data was 
        provided by JMA.


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
        """ % (timestamp, argv["channel"], dataRegionDesc)
        text = text.strip().split('\n')
        
        for line in text:
            envDraw.text((envL, envT), line.strip(), font=font, fill="black")
            envT += textH * 1.5

        if argv["scale"]:
            imgScaleBarW, imgScaleBarH = 200, 1024
            imgScaleBar = Image.new('RGB', (imgScaleBarW, imgScaleBarH))
            imgScaleBarDraw = ImageDraw.Draw(imgScaleBar)
            for i in xrange(0, imgScaleBarH):
                fill = int(i * 255.0 / imgScaleBarH)
                fill = "rgb(%d,%d,%d)" % (fill, fill, fill)
                imgScaleBarDraw.line([(0, i), (imgScaleBarW, i)], fill=fill, width=1)
            imgScaleBarLT = (\
                w + margin * 2,
                imgEnvSize[1] - margin - imgScaleBarH
            )
            imgScaleBarRegion = (\
                imgScaleBarLT[0],
                imgScaleBarLT[1],
                imgScaleBarLT[0] + imgScaleBarW,
                imgScaleBarLT[1] + imgScaleBarH
            )
            imgEnv.paste(imgScaleBar, imgScaleBarRegion)

            # left top of the text area
            textLT = (\
                imgScaleBarLT[0] + imgScaleBarW + textW,
                imgScaleBarLT[1]
            )

            # text min value
            minValue = "%-5.2f %s" % (argv["scale"][0], self.colorScaleUnit)
            envDraw.text(\
                (textLT[0], imgScaleBarLT[1]),
                minValue,
                font=font,
                fill="black"
            )

            # text max value
            maxValue = "%-5.2f %s" % (argv["scale"][1], self.colorScaleUnit)
            envDraw.text(\
                (textLT[0], textLT[1] + imgScaleBarH - textH),
                maxValue,
                font=font,
                fill="black"
            )
                
        # done
        return imgEnv, imgDataRegion


if __name__ == '__main__':
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

    source = open('testdata/sample.geoss', 'r').read()

    p = plotter()
    p.setScaleParameters(True, 'K')
    p.setConvertTable(convert)
    p.setSourceRegion(59.98, 85.02, -60.02, -154.98)
    p.setDataDimension(3000, 3000)
    p.setDK('1')
    p.setDataResolution(0.04, 0.04)

    print "Plotting data..."
    img, scaleInfo = p.plotData(source)

#   print "Adding coastlines..."
#    img = p.plotCoastlines(img)

    print "Adding coordinate lines..."
    img = p.plotCoordinateLines(img)

    print "Packing image..."
    img, imgRegion = p.packImage(img, timestamp='201411181531', channel='IR1', scale=scaleInfo)

    img.save('output.png')
    exit()
                

            
"""
##############################################################################
# grey image adjust
        #img = ImageOps.invert(img) // using new scale of color, not useful
actualDrawX1, actualDrawY1 = toPlotXY(actualDrawLatMax, actualDrawLngMin)
actualDrawX2, actualDrawY2 = toPlotXY(actualDrawLatMin, actualDrawLngMax)

imgCropRegion = (int(actualDrawX1), int(actualDrawY1), int(actualDrawX2), int(actualDrawY2))
imgCrop = img.crop(imgCropRegion)
imgCrop = ImageOps.equalize(imgCrop)
img.paste(imgCrop, imgCropRegion)

# enhance constrast
#contrastEnhancer = ImageEnhance.Contrast(img)
#contrastEnhancer.enhance(10)

# brightness enhancer
brightnessEnhancer = ImageEnhance.Brightness(img)
brightnessEnhancer.enhance(0.5)
"""
