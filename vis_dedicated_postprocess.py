#!/usr/bin/python

import sys
import os

def postProcess(img, p):

    print "> Adding coastlines..."
    img = p.plotCoastlines(img, 0) #, "rgb(255,0,0)")

    #print "> Adding cities..."
    #img = p.plotCities(img, 0, 14) #, "rgb(255,0,0)")

    print "> Crop image..."
    img = p.crop(img, (85.0, 85.0, 0.0, 145.0))

    print "> Equalize image..."
    img = p.equalize(img)


    #print "> Adding coordinate lines..."
    #img = p.plotCoordinate(img)

    return img
