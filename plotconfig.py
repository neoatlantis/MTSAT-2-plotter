drawData = True
drawCoastline = True

projectionMethod = 'equirectangular'

markRegion = [
    {"region": [(25.8 - 17.966, 110.0 - 20), (25.8 + 17.966, 110.0 + 20)], "center": True},
]

# set the actual drawn region. may not be the whole image, in order to save
# time
cropLatN = 25.8 + 17.966 
cropLatS = 25.8 - 17.966 
cropLngDiffW = 110.0 - 20.0
cropLngDiffE = 110.0 + 20.0

