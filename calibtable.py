import array
import os
import sys

def getCalibrationTable(bandName, bandNumber):
    bandName = bandName.lower()
    assert (bandName, bandNumber) in [\
        ('ext', 1),
        ('vis', 1), ('vis', 2), ('vis', 3),
        ('sir', 1), ('sir', 2),
        ('tir', 1), ('tir', 2), ('tir', 3), ('tir', 4), ('tir', 5), ('tir', 6),
        ('tir', 7), ('tir', 8), ('tir', 9), ('tir', 10)
    ]
    PATH = os.path.realpath(os.path.dirname(sys.argv[0]))
    curve = open(os.path.join(\
        PATH, 'calibration_table', '%s.%02d' % (bandName, bandNumber)
    ), 'r').read().strip().split('\n')
    curveListRaw = [v.strip().split(' ') for v in curve]
    curveList = [(int(v[0]), float(v[1])) for v in curveListRaw]
    table = [-9999] * 65536
    for x, y in curveList: table[x] = y
    return table 

if __name__ == '__main__':
    print "Test calibtable generation"
    print getCalibrationTable('tir', 10)
