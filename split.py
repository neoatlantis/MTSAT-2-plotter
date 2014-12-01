#!/usr/bin/python

import os
import sys
import math

from PIL import Image

from plotconfig import splitXInc, splitYInc


def splitter(p, fn, img=None):
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

    for zoomLevel in xrange(3, 6):
        count = 2 ** zoomLevel
        gridDegreeX = 360.0 / count
        gridDegreeY = 180.0 / count

        for x in xrange(0, count):
            cropW = x * gridDegreeX - 180
            cropE = cropW + gridDegreeX
            
            outPath = os.path.join(\
                pathBase,
                fileName + '-split',
                str(zoomLevel),
                str(x)
            )
            try:
                os.makedirs(outPath)
            except Exception,e:
                print e
                print outPath
                continue

            cropS = 90.0
            for y in xrange(0, count):
                cropS -= gridDegreeY
                cropN = cropS + gridDegreeY
                try:
                    crop = p.cropAndResize(img, (cropN, cropW, cropS, cropE))
                except:
                    print (cropN, cropW, cropS, cropE)
                    continue
                if crop:
                    crop = crop.convert("RGB")
                    crop.save(os.path.join(outPath, str(y) + '.jpg'))
