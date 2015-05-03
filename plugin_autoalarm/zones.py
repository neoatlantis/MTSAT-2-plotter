# -*- coding: utf-8 -*-

zones = {}


ASLAB_CENTER_LAT = 25.798
ASLAB_CENTER_LNG = 110.013

zones["ASLAB"] = {
    "40km": {
        "title": u"越城岭天文台半径 40km IR1 红外云图",
        "region": ((ASLAB_CENTER_LAT+0.36, ASLAB_CENTER_LNG-0.4), (ASLAB_CENTER_LAT-0.36, ASLAB_CENTER_LNG+0.4)),
        "alarm": {
            "Tbb": {
                "threshold": -30.0,
                "percent": 50.0,
                "name": u"测试信号A"
            }
        },
    },
    "100km": {
        "title": u"越城岭天文台半径 100km IR1 红外云图",
        "region": ((ASLAB_CENTER_LAT+0.9, ASLAB_CENTER_LNG-1), (ASLAB_CENTER_LAT-0.9, ASLAB_CENTER_LNG+1)),
        "alarm": {
            "Tbb": {
                "threshold": -50.0,
                "percent": 20.0,
                "name": u"测试信号B"
            }
        },
    },
    "400km": {
        "title": u"越城岭天文台半径 400km IR1 红外云图",
        "region": ((ASLAB_CENTER_LAT+3.6, ASLAB_CENTER_LNG-4), (ASLAB_CENTER_LAT-3.6, ASLAB_CENTER_LNG+4)),
        "alarm": {
            "Tbb": {
                "threshold": -50.0,
                "percent": 5.0,
                "name": u"测试信号C"
            }
        },
    },
    "800km": {
        "title": u"越城岭天文台半径 800km IR1 红外云图",
        "region": ((ASLAB_CENTER_LAT+7.3, ASLAB_CENTER_LNG-8), (ASLAB_CENTER_LAT-7.3, ASLAB_CENTER_LNG+8)),
        "alarm": {
            "Tbb": {
                "threshold": -50.0,
                "percent": 10.0,
                "name": u"测试信号D"
            }
        },
    },
}
