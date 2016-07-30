import math

def hsvToRgb(h, s, v):
    h /= 360.0
    s /= 100.0
    v /= 100.0

    i = round(math.floor(h * 6.0)) % 6
    f = h * 6.0 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    if i == 0:   r,g,b = v,t,p
    elif i == 1: r,g,b = q,v,p
    elif i == 2: r,g,b = p,v,t
    elif i == 3: r,g,b = p,q,v
    elif i == 4: r,g,b = t,p,v
    elif i == 5: r,g,b = v,p,q

    return (round(r * 255.0), round(g * 255.0), round(b * 255.0))

##############################################################################
def FIRE(T):
    detect = 320.0
    if T <= 180:
        h, s, v = 0, 0, 100
    elif T <= detect:
        h, s = 0, 0
        v = 100 - 55.0 * (T - 180) / (detect - 180)
    elif T <= 360:
        #60, 100, 100 ===> 0, 100, 100
        s, v = 100, 100
        h = 60 - (T - detect) * 60.0 / (360 - detect)
    else:
        h, s, v = 0, 100, 100

    return hsvToRgb(h, s, v)
        

def NRL(T):
    i = T - 273.15
    h, s, v = 0, 100, 100
    if i < -80:
        h, s = 36 + 2.4 * (i + 90), 85 + 1.5 * (i + 90)
    elif i <= -70:
        h = 30 - 3.0 * (i + 80)
        s = 75 + 2.5 * (i + 80)
        v = 60 + 4.0 * (i + 80)
    elif i < -50:
        h = 120 - 1.5 * (i + 70)
        s = 100
        v = 60 + 2.0 * (i + 70)
    elif i < -30:
        h = 240 - 2.5 * (i + 50)
        s = 100
        v = 70 + 1.5 * (i + 50)
    elif i < 30: 
        h = 0
        s = 0
        v = 100 - 100 * (i + 30) / 60.0
    else:
        h, s, v = 0, 0, 0

    return hsvToRgb(h, s, v)

def IRBD(T):
    h, s, v = 0, 0, 100
    i = T - 273.15

    if i <= -81: v = 26
    elif i <= -76: v = 62
    elif i <= -70: v = 100
    elif i <= -64: v = 0
    elif i <= -54: v = 72
    elif i <= -42: v = 60
    elif i <= -31: v = 36
    elif i <= 9: v = 82 + (23 - 82) * (i + 30) / 39
    elif i <= 27: v = 100 + (0 - 100) * (i - 9) / (27 - 9)
    else: v = 0

    return hsvToRgb(h, s, v)

def IRWV(T):
    h, s, v = 0, 0, 100
    i = T - 273.15

    if i < -70: i = -70
    if i > 0: i = 0

    if i <= -60: 
        h = 2.4 * (i + 70)
        s = 100
        v = 50 + 3.5 * (i + 70)
    elif i <= -50:
        h = 24 + 1.2 * (i + 60)
        s = 100 - 2.5 * (i + 60)
        v = 85 + 1.5 * (i + 60)
    elif i <= -40:
        h = 36 + 4.4 * (i + 50)
        s = 75 - 2.5 * (i + 50)
    elif i <= -30:
        h = 80 + 8 * (i + 40)
        s = 50
    elif i <= -20:
        h = 160 + 4 * (i + 30)
        s = 50 + 3 * (i + 30)
    elif i <= -10:
        h = 200 + 2 * (i + 20)
        s = 80 + 0.5 * (i + 20)
        v = 100 - 1.5 * (i + 20)
    elif i <= 0:
        h = 220 + 8 * (i + 10)
        s = 85 + 1.5 * (i + 10)
        v = 85 - 3.5 * (i + 10)

    return hsvToRgb(h, s, v)

def VIS(albedo):
    if albedo < 20.0: return (0, 0, 0)
    i = int(round((albedo - 20.0) * 2.0))
    return (i, i, i)

##############################################################################

def generatePPMColorscale(converter, scaleName):
    if converter.value == 'Tbb':
        assert scaleName in ['NRL', 'IRBD', 'IRWV', 'FIRE'] #, 'CycloneCenter']
    else:   
        assert scaleName in ['VIS']

    mapper = {
        'NRL': NRL, 'IRBD': IRBD, 'IRWV': IRWV, 'FIRE': FIRE,
        'VIS': VIS,
    }

    ret = 'P3\n# colorscale\n256 1\n255\n'
    for i in xrange(0, 256):
        pvalue = converter.greyscaleToPhysic(i)
        ret += '%d %d %d  ' % (mapper[scaleName](pvalue)) 

    return ret
