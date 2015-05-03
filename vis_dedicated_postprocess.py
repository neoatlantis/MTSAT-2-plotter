#!/usr/bin/python

import sys
import os

def postProcess(img, p):

    print "> Adding China boundaries..."
    img = p.plotChina(img, 0) #, "rgb(255,0,0)")

    #print "> Adding coastlines..."
    #img = p.plotCoastlines(img, 0) #, "rgb(255,0,0)")

    print "> Adding province borders..."
    img = p.plotProvinces(img, 0)

    #print "> Adding cities..."
    #img = p.plotCities(img, 0, 14) #, "rgb(255,0,0)")

    print "> Crop image..."
    img = p.crop(img, (85.0, 85.0, 0.0, 145.0))
    #img = p.crop(img, (35.0, 120.0, 25.0, 135.0)) # N W S E

    print "> Equalize image..."
    img = p.equalize(img)

    return img
