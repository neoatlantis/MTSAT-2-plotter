#!/usr/bin/python
"""
NeoAtlantis MTSAT-2 Lightweighted Data Plotter and Cropper
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
import math
import converter
##############################################################################

class plotter:

    coeff = math.pi / 180.0
    
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

        # TODO following loop is slow, fix it.
        curveLen = len(curve)
        for x in xrange(0, tableSize):
            for i in xrange(0, curveLen):
                if x >= curve[i][0] and x <= curve[i+1][0]:
                    break
            left, right = curve[i], curve[i+1]
            value = 1.0 * (x - left[0]) / (right[0] - left[0])
            value *= (right[1] - left[1])
            value += left[1]
            self.lookupTable[x] = self.__getColorScale(value)

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

    def setColorScale(self, colorScale):
        self.colorScale = colorScale;

    def _getPaintColor(self, uint16):
        # Convert the satellite result, which is Uint16, into Uint8 gray scale
        # color. This is done by simply looking up the lookup table
        # precalculated.
        return self.lookupTable[uint16]

    def __getColorScale(self, value):
        return self.colorScale.getPaletteColor(value)

    def __withinSourceRegion(self, lat, lng):   
        srcLatN, srcLngW, srcLatS, srcLngE = self.sourceRegion
        if lat > srcLatN or lat < srcLatS:
            return False
        if srcLngW <= srcLngE:
            return (lng >= srcLngW and lng <= srcLngE)
        else:
            if lng<0:
                lng += 360
            return (lng >= srcLngW and lng <= 360 + srcLngE)

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
        
        dataSize = self.dataDimension[0] * self.dataDimension[1]
        imgPStr = converter.convert(\
            self.lookupTable, self.dataDimension, dataString
        )
        # maxGray, minGray = extremeValues

        imgP = Image.fromstring('P', self.dataDimension, imgPStr)
        imgP.putpalette(self.colorScale.PALETTE)
        return imgP

    def cropAndResize(self, img, cropRegion):
        cropN, cropW, cropS, cropE = cropRegion
        drawW, drawH = self.dataDimension
        outW, outH = 256, 256

        pointLT = self.__project(cropN, cropW)
        pointRB = self.__project(cropS, cropE)
        pointL, pointT = pointLT
        pointR, pointB = pointRB
        cropPointW, cropPointH = pointR - pointL, pointB - pointT
        if cropPointW <= 0 or cropPointH <= 0:
            raise Exception('Wrong parameter specified!')

        # see if the region is inside our image, otherwise return None
        if (0 - pointL) * (drawW - pointL) > 0 and (0 - pointR) * (drawW - pointR) > 0:
            return None
        if (0 - pointT) * (drawH - pointT) > 0 and (0 - pointB) * (drawH - pointB) > 0:
            return None 

        newImage = Image.new('P', (cropPointW, cropPointH), 0)
        
        pasteX, pasteY = 0, 0
        if pointR > drawW:
            pointR = drawW
        if pointB > drawH:
            pointB = drawH
        if pointL < 0:
            pasteX = -pointL
            pointL = 0
        if pointT < 0:
            pasteY = -pointT
            pointT = 0

        cropImage = img.crop((pointL, pointT, pointR, pointB))
        newImage.paste(cropImage, (pasteX, pasteY))
        newImage = newImage.resize((outW, outH))
        newImage.putpalette(self.colorScale.PALETTE)
        return newImage
        
        


if __name__ == '__main__':
    convert = """
    0:=329.98
    30:=327.62
    60:=325.21
    89:=322.85
    117:=320.52
    144:=318.25
    171:=315.94
    197:=313.67
    222:=311.45
    247:=309.20
    271:=307.00
    294:=304.85
    317:=302.66
    339:=300.53
    360:=298.46
    381:=296.36
    401:=294.32
    421:=292.24
    440:=290.22
    459:=288.17
    477:=286.19
    495:=284.17
    512:=282.22
    529:=280.24
    545:=278.34
    561:=276.40
    576:=274.54
    591:=272.64
    605:=270.84
    619:=269.00
    632:=267.25
    645:=265.47
    658:=263.66
    670:=261.94
    682:=260.20
    694:=258.41
    705:=256.73
    716:=255.02
    727:=253.28
    737:=251.65
    747:=249.99
    757:=248.29
    766:=246.73
    775:=245.13
    784:=243.49
    792:=242.00
    800:=240.48
    808:=238.93
    816:=237.33
    823:=235.91
    830:=234.45
    837:=232.95
    844:=231.42
    850:=230.08
    856:=228.70
    862:=227.30
    868:=225.85
    874:=224.37
    879:=223.11
    884:=221.82
    889:=220.50
    894:=219.14
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
    947:=201.94
    950:=200.75
    953:=199.52
    956:=198.26
    959:=196.95
    962:=195.61
    964:=194.69
    966:=193.74
    968:=192.78
    970:=191.79
    972:=190.77
    974:=189.73
    976:=188.65
    978:=187.54
    980:=186.40
    982:=185.23
    983:=184.62
    984:=184.01
    985:=183.38
    986:=182.75
    987:=182.10
    988:=181.44
    989:=180.76
    990:=180.07
    991:=179.37
    992:=178.65
    993:=177.92
    994:=177.17
    995:=176.40
    996:=175.61
    997:=174.80
    998:=173.97
    999:=173.12
    1000:=172.24
    1001:=171.34
    1002:=170.40
    1003:=169.44
    1004:=168.45
    1005:=167.41
    1006:=166.34
    1007:=165.23
    1008:=164.06
    1009:=162.85
    1010:=161.58
    1011:=160.24
    1012:=158.82
    1013:=157.32
    1014:=155.73
    1015:=154.01
    1016:=152.16
    1017:=150.15
    1018:=147.93
    1019:=145.45
    1020:=142.63
    1021:=139.32
    1022:=135.29
    1023:=130.02
    65535:=130.02
    """
    from colorscale import Grayscale as COLORSCALE_IR

    source = open('testdata/sample.geoss', 'r').read()

    p = plotter()
    p.setColorScale(COLORSCALE_IR)
    p.setConvertTable(convert)
    p.setSourceRegion(59.98, 85.02, -60.02, -154.98)
    p.setDataDimension(3000, 3000)
    p.setDK('1')
    p.setDataResolution(0.04, 0.04)

    print "Plotting data..."
    img = p.plotData(source)

    print "Adding coastlines..."
    img = p.plotCoastlines(img)

#    print "Adding coordinate lines..."
#    img = p.plotCoordinate(img)

    img.save('output.png')

    crop = p.cropAndResize(img, (1.40625, 140-1.40625, -1.40625, 140+1.40625)).convert("RGB")
    if crop:
        crop.save('crop.jpg')
    else:
        print "Crop region not inside our image."