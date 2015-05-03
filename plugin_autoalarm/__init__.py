# -*- coding: utf-8 -*-

import os
import sys
import math

PUBLISH_PATH = '/var/www/lab/'

from PIL import Image, ImageDraw, ImageFont

from zones import zones
from IR_COLOR import PALETTE as IRCOLOR_PALETTE
from IR_COLOR import getPaletteColor



getTbbFromGrayscale = lambda g: g / 2.0 - 90.0
# ... in celsius grads, see `../colorscale/Grayscale` for definition

def processImage(img, **argv):
    data = ''.join([chr(i) for i in list(img.getdata())])
    newimg = Image.fromstring('P', img.size, data)
    newimg.putpalette(IRCOLOR_PALETTE)
    newimg = newimg.convert('RGB')
    ########## get dimensions
    channelName = argv["channel"]
    if channelName == 'IR': # scale at IR mode is 4 km each pixel
        satX, satY = 4.0, 4.0
    else:                   # scale at VIS mode is 1 km each pixel
        satX, satY = 1.0, 1.0
    w, h = newimg.size
    realW, realH = satX * w, satY * h # estimated represented geo. size in kilometers
    w2, h2 = w/2.0, h/2.0
    ########## resize image
    tw, th = 512, 512
    ratioX, ratioY = tw / w, th / h # enlargement ratio
    newimg = newimg.resize((tw, th))
    ########## prepare for draw on image
    imgDraw = ImageDraw.Draw(newimg)
    tw2 = tw/2
    th2 = th/2
    blue = "rgb(0,0,127)"
    white = "rgb(255,255,255)"
    black = "rgb(0,0,0)"
    orange = "rgb(255,127,0)"
    ########## draw center cross
    size = 6
    width = 3
    imgDraw.line([(tw2 - size, th2), (tw2 + size, th2)], fill=blue, width=width)
    imgDraw.line([(tw2, th2 - size), (tw2, th2 + size)], fill=blue, width=width)
    ########## draw scale ruler
    rulerRealXLen = 10 ** math.floor(math.log(realW / 5.0, 10))
    rulerDrawXLen = rulerRealXLen / satX * ratioX 
    replicate = math.floor(tw / 5.0 / rulerDrawXLen) # adjust choosen ruler length to something near 1/5 the width
    rulerRealXLen *= replicate
    rulerDrawXLen *= replicate
    rulerY = th * 0.95
    rulerXL = tw * 0.95 - rulerDrawXLen
    rulerXR = tw * 0.95
    rulerXC = 0.5 * (rulerXL + rulerXR)
    imgDraw.line([(rulerXL, rulerY), (rulerXR, rulerY)], fill=white, width=width)
    imgDraw.line([(rulerXL, rulerY+width), (rulerXR, rulerY+width)], fill=black, width=width)
    ########## mark scale ruler text
    text = "%d km" % rulerRealXLen
    font = ImageFont.truetype('resources/font.ttf', size=12, encoding="unic")
    textsizeW, textsizeH = font.getsize(text)
    textL = rulerXC - textsizeW / 2.0
    textT1 = rulerY - textsizeH * 1.5
    textT2 = rulerY + width + textsizeH * 0.5
    imgDraw.text((textL, textT1), text, font=font, fill=white)
    imgDraw.text((textL, textT2), text, font=font, fill=black)
    ########## mark other information for the picture
    font = ImageFont.truetype('resources/font.ttf', size=10, encoding="unic")
    divideTime = lambda s:s[0:4] + '-' + s[4:6] + '-' + s[6:8] + ' ' + s[8:10] + ':' + s[10:12]
    lines = [
        u'标题: %s' % argv["title"],
        u'时刻: %s UTC' % divideTime(argv["time"]),
        u'制图: NeoAtlantis应用科学与神秘学实验室',
        u'* MTSAT2数据来自日本千叶大学环境遥感中心',
        u'* 原始数据由JMA提供',
    ]
    maxTextW, maxTextH = 0, 0
    for each in lines:
        textW, textH = font.getsize(each)
        maxTextW = max(maxTextW, textW)
        maxTextH = max(maxTextH, textH)
    infoXB, infoYB = 0.01 * tw, 0.01 * th
    infoXL = infoXB
    infoXC = infoXL + maxTextW / 2.0
    infoY = infoYB
    infoYInc = maxTextH * 1.1
    imgDraw.rectangle((0, 0, infoXB * 2 + maxTextW, maxTextH * len(lines) + 2 * infoYB), outline=black, fill=white)
    for each in lines:
        textW, textH = font.getsize(each)
        imgDraw.text((infoXL, infoY), each, font=font, fill=black)
        infoY += infoYInc
    ########## mark alarms
    font = ImageFont.truetype('resources/font.ttf', size=12, encoding="unic")
    lines = argv["alarms"]
    if len(lines) > 0:
        lines.insert(0, u"建议考虑:")
        maxTextW, maxTextH = 0, 0
        for each in lines:
            textW, textH = font.getsize(each)
            maxTextW = max(maxTextW, textW)
            maxTextH = max(maxTextH, textH)
        infoXB, infoYB = 0.01 * tw, 0.01 * th
        infoXL = infoXB
        infoXC = infoXL + maxTextW / 2.0
        infoY = th - infoYB - maxTextH
        infoYInc = maxTextH * 1.1
        imgDraw.rectangle((0, th, infoXB * 2 + maxTextW, th - maxTextH * len(lines) - 2 * infoYB), outline=black, fill=orange)
        lines.reverse()
        for each in lines:
            textW, textH = font.getsize(each)
            imgDraw.text((infoXL, infoY), each, font=font, fill=black)
            infoY -= infoYInc
    ########## make a colorscale display
    TbbMin = -90.0
    TbbMax = +30.0
    colorscaleH = 20
    textH = font.getsize(u'0')[1] * 1.2
    colorscaleImg = Image.new('P', (tw, int(colorscaleH + textH)))
    colorscaleImg.putpalette(IRCOLOR_PALETTE)
    colorscaleDraw = ImageDraw.Draw(colorscaleImg)
    for i in xrange(0, tw):
        Tbb = float(i) / tw * (TbbMax - TbbMin) + TbbMin + 273.15
        color = getPaletteColor(Tbb)
        colorscaleDraw.line([(i, textH), (i, colorscaleH+textH)], fill=color, width=1)
    colorscaleImg = colorscaleImg.convert('RGB')
    colorscaleDraw = ImageDraw.Draw(colorscaleImg)
    colorscaleDraw.rectangle((0, 0, tw, textH), fill=white)
    Tbb = TbbMin
    while Tbb <= TbbMax:
        text = '%d' % Tbb
        textW, textH = font.getsize(text)
        textL = (Tbb - TbbMin) / (TbbMax - TbbMin) * tw
        colorscaleDraw.text((textL - textW / 2.0, 0.1 * textH), text, font=font, fill=black)
        Tbb += 10
    ########## join 2 images(colorscale and plot) together
    cw, ch = colorscaleImg.size
    resimg = Image.new('RGB', (tw, th + ch))
    resimg.paste(newimg, (0, 0, tw, th))
    resimg.paste(colorscaleImg, (0, th, tw, th+ch))

    return resimg

def checkAlarm(img, alarm):
    result = []
    if alarm.has_key("Tbb"):
        TbbRule = alarm["Tbb"]
        print "#1"
        threshold = TbbRule["threshold"]
        percent = TbbRule["percent"]
        hgram = img.histogram()
        total = sum(hgram)
        count = 0
        for g in xrange(0, len(hgram)):
            if getTbbFromGrayscale(g) <= threshold:
                count += hgram[g]
        calcPercent = count * 1.0 / (total * 1.0) * 100.0
        if calcPercent >= percent: result.append(alarm["Tbb"]["name"])
    return result 


def plugin_autoalarm(**argv):
    if argv["channel"] != "IR1": return
    p = argv["plotter"]
    imgP = argv["image"]
    imgP = p.plotChina(imgP, 0, 1)

    for zoneName in zones:
        for regionName in zones[zoneName]:
            region = zones[zoneName][regionName]
            regionNW, regionSE = region["region"]
            regionN, regionW = regionNW
            regionS, regionE = regionSE
            regionRawImgP = p.crop(imgP, (
                regionN, regionW, regionS, regionE
            ))

            alarmCheck = []
            if region.has_key("alarm"):
                regionAlarm = region["alarm"]
                alarmCheck = checkAlarm(regionRawImgP, regionAlarm)
            regionColorified = processImage(regionRawImgP, channel='IR', time=argv["time"], title=region["title"], alarms=alarmCheck)
            regionFilename = '%s.%s.png' % (zoneName, regionName)
            regionPathname = os.path.join(PUBLISH_PATH, regionFilename)
            regionColorified.save(regionPathname)
    return


if __name__ == "__main__":
    print 'hello'
    pass
