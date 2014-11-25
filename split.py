#!/usr/bin/python

import os
import sys
import math

from PIL import Image

from plotconfig import splitXInc, splitYInc


def splitter(fn, img=None):
    try:
        fileFullName = os.path.realpath(fn)
    except:
        raise Exception('File to be treated not given.')

    pathBase = os.path.realpath(os.path.dirname(fileFullName))
    fileName = os.path.basename(fileFullName)

    outPath = os.path.join(pathBase, fileName + '-split')
    indexFile = os.path.join(outPath, 'index.txt')

    try:
        os.makedirs(outPath)
    except:
        pass

    try:
        open(indexFile, 'w+').write('')
    except:
        raise Exception('Unable to create index file.')

    print "> Crop image at %s" % fileFullName

    if None == img:
        img = Image.open(fileFullName)
        print "> Read in image."

    imgW, imgH = img.size

    xBlocks = int(math.ceil(imgW * 1.0 / splitXInc))
    yBlocks = int(math.ceil(imgH * 1.0 / splitYInc))

    print "> Will split the image into %d blocks." % (xBlocks * yBlocks)

    for yi in xrange(0, yBlocks):
        for xi in xrange(0, xBlocks):
            startX, startY = xi * splitXInc, yi * splitYInc
            endX, endY = startX + splitXInc, startY + splitYInc
            if endX > imgW:
                endX = imgW
            if endY > imgH:
                endY = imgH
            print "> Creating the block at (%d, %d)..." % (xi, yi)

            imgCrop = img.crop((startX, startY, endX, endY))
            saveName = "%d:%d.jpg" % (startX, startY)
            saveFullName = os.path.join(outPath, saveName)

            imgCrop.save(saveFullName, quality=90, optimize=True)
            print "> File saved to: %s" % saveFullName

            logStr = "%s\t(%d,%d)\t(%d,%d)\n" % (saveName, startX, startY, endX, endY)
            open(indexFile, 'a+').write(logStr)

            print "> Log: %s" % logStr


if __name__ == '__main__':
    try:
        splitter(sys.argv[1])
    except Exception,e:
        print e
        sys.exit(1)
