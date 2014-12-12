#!/usr/bin/python

import os
import sys
import math

from PIL import Image

from plotconfig import splitXInc, splitYInc


def splitter(p, fn, img=None, maxZoom=6, onlyJPG=False):
    onlyJPG = False
    try:
        fileFullName = os.path.realpath(fn)
    except:
        raise Exception('File to be treated not given.')

    pathBase = os.path.realpath(os.path.dirname(fileFullName))
    fileName = os.path.basename(fileFullName)

    print "> Crop image at %s" % fileFullName

    if None == img:
        img = Image.open(fileFullName)
        print "> Read in image."

    for zoomLevel in xrange(4, maxZoom + 1):
        count = (1 << zoomLevel)
        gridDegreeX = 360.0 / count
        gridDegreeY = 360.0 / count

        for x in xrange(0, count):
            cropW = x * gridDegreeX - 180
            cropE = cropW + gridDegreeX
            
            outPath = os.path.join(\
                pathBase,
                fileName + '-split',
                str(zoomLevel),
                str(x)
            )
            outPathCreated = False

            cropS = 180.0  # who knows how the developer of Leaflet.js thought
            for y in xrange(0, count):
                cropS -= gridDegreeY 
                cropN = cropS + gridDegreeY

                if abs(cropN) > 90.0:
                    continue

                try:
                    crop = p.cropAndResize(img, (cropN, cropW, cropS, cropE))
                except:
#                   print (cropN, cropW, cropS, cropE)
                    continue
                if not crop:
                    continue

                imgFormat = '.png'
                if onlyJPG == True or zoomLevel <= maxZoom - 1:
                    crop = crop.convert("RGB")
                    imgFormat = '.jpg'

                if not outPathCreated: 
                    try:
                        os.makedirs(outPath)
                        outPathCreated = True
                    except Exception,e:
                        print e
                        print outPath
                        continue

                if outPathCreated:
                    crop.save(\
                        os.path.join(outPath, str(y) + imgFormat),
                        quality=70
                    )
