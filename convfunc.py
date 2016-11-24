class TbbConverter:
    value = 'Tbb'
    minTbb = -90.0
    maxTbb = +30.0
    possibleColorscales = ['NRL', 'IRBD', 'IRWV']
    def physicToGreyscale(self, Tbb):
        Tbb = Tbb - 273.15
        if Tbb < self.minTbb: Tbb = self.minTbb
        if Tbb > self.maxTbb: Tbb = self.maxTbb
        return int(round((Tbb - self.minTbb) * 2.125))# 2.125 = 255 / [30 - (-90)]
    def greyscaleToPhysic(self, g):
        if g < 0: g = 0
        if g > 255: g = 255
        return g / 2.125 + self.minTbb + 273.15

class AlbedoConverter:
    value = 'albedo'
    minAlbedo = -2
    maxAlbedo = +120.0
    possibleColorscales = ['VIS']
    def physicToGreyscale(self, albedo):
        if albedo < self.minAlbedo: albedo = self.minAlbedo
        if albedo > self.maxAlbedo: albedo = self.maxAlbedo
        return int(round((albedo - self.minAlbedo) * 2.09)) # 2.09= 255 / [120 - (-2)]
    def greyscaleToPhysic(self, g):
        if g < 0: g = 0
        if g > 255: g = 255
        return g / 2.09 + self.minAlbedo
        

def getConverter(bandName, bandNumber):
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
    if (bandName, bandNumber) in TbbConvInputs: return TbbConverter
    elif (bandName, bandNumber) in AlbedoInputs: return AlbedoConverter
    else: raise Exception("Invalid band specification.")
