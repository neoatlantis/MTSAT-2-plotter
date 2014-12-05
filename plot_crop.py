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
import os
import sys
from subprocess import call
import uuid
import math

from headerFileReader import extractConvertTable
##############################################################################

class plotter:

    coeff = math.pi / 180.0
    
    def __init__(self):
        tn = str(uuid.uuid4())
        dn = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.__tempFolder = os.path.join(dn, 'temp', tn)
        call(['mkdir', '-p', self.__tempFolder])

    def __clear__(self):
        # remove cached files
        dn = os.path.dirname(os.path.realpath(sys.argv[0]))
        if not self.__tempFolder.startswith(dn):
            return
        call(['rm', '-rf', self.__tempFolder])

    def getCacheFilename(self, name=None):
        if name == None:
            name = str(uuid.uuid4())
        return os.path.join(self.__tempFolder, name)

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

    def __getColorScale(self, value):
        return self.colorScale.getPaletteColor(value)

    def __getConvertTable(self, convert):
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
        lookupTable = [0,] * tableSize

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
            lookupTable[x] = self.__getColorScale(value)
        return ''.join([chr(i) for i in lookupTable])

    def __project(self, lat, lng):
        if lng < 0:
            lng += 360
        lngDiff = lng - self.sourceRegion[1] # lng - srcLngW
        drawX = lngDiff / self.dataResolution[1]
        drawY = self.dataDimension[1] / 2 - lat / self.dataResolution[0]
        return int(drawX), int(drawY)

    def plotData(self, dataFilename, headerFilename):
        self.imageFilename = self.getCacheFilename()
        print "Writing PGM header..."
        open(self.imageFilename, 'w+').write(\
            'P5\n#\n%d %d\n255\n' % self.dataDimension
        )

        print "Writing convert tables..."
        header = open(headerFilename, 'r').read()
        convert = extractConvertTable(header)
        convertTableStr = self.__getConvertTable(convert)
        convertTableName = self.getCacheFilename()
        open(convertTableName, 'w+').write(convertTableStr)
        del convertTableStr
        del convert
       
        print "Calling C converter..."
        cmd = "cat %s %s | ./converter >> %s" % (\
            convertTableName, dataFilename, self.imageFilename
        )
        print cmd
        call(cmd, shell=True)
        print "C converter called."
        return os.path.isfile(self.imageFilename)

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
    from colorscale import Grayscale as COLORSCALE_IR

    source = 'testdata/sample.geoss'
    header = 'testdata/sample.txt'

    p = plotter()
    p.setColorScale(COLORSCALE_IR)
    p.setSourceRegion(59.98, 85.02, -60.02, -154.98)
    p.setDataDimension(3000, 3000)
    p.setDK('1')
    p.setDataResolution(0.04, 0.04)

    print "Plotting data..."
    img = p.plotData(source, header)
    print img
    exit()

    img.save('output.png')

    crop = p.cropAndResize(img, (1.40625, 140-1.40625, -1.40625, 140+1.40625)).convert("RGB")
    if crop:
        crop.save('crop.jpg')
    else:
        print "Crop region not inside our image."

    p.__clear__()
