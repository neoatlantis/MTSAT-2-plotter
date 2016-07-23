def getConversionFunction(bandName, bandNumber):
    bandName = bandName.lower()
    TbbConvInputs = [
        ('tir', 1), ('tir', 2), ('tir', 3), ('tir', 4), ('tir', 5), ('tir', 6),
        ('tir', 7), ('tir', 8), ('tir', 9), ('tir', 10)
    ]
    AlbedoInputs = [
        ('ext', 1),
        ('vis', 1), ('vis', 2), ('vis', 3),
        ('sir', 1), ('sir', 2),
    ]
    if (bandName, bandNumber) in TbbConvInputs:
        def conv(Tbb):
            minTbb = -90.0
            maxTbb = +30.0
            Tbb = Tbb - 273.15
            if Tbb < minTbb: Tbb = minTbb
            if Tbb > maxTbb: Tbb = maxTbb
            return int(round((Tbb - minTbb) * 2.125))# 2.125 = 255 / [30 - (-90)]

    elif (bandName, bandNumber) in AlbedoInputs:
        def conv(albedo):
            minAlbedo = -2
            maxAlbedo = +120.0
            if albedo < minAlbedo: albedo = minAlbedo
            if albedo > maxAlbedo: albedo = maxAlbedo
            return int(round((albedo - minAlbedo) * 2.09)) # 2.09= 255 / [120 - (-2)]

    else:
        raise Exception("Invalid band specification.")

    return conv
