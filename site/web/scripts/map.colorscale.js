define([], function(){
//////////////////////////////////////////////////////////////////////////////

var ret = {};

function round(color){
    var r = Math.round(color);
    if(r > 255) r = 255;
    if(r < 0) r = 0;
    return r;
};

/**
 * Converts an HSV color value to RGB. Conversion formula
 * adapted from http://en.wikipedia.org/wiki/HSV_color_space.
 * Assumes h, s, and v are contained in the set [0, 1] and
 * returns r, g, and b in the set [0, 255].
 *
 * @param   Number  h       The hue
 * @param   Number  s       The saturation
 * @param   Number  v       The value
 * @return  Array           The RGB representation
 */
function hsvToRgb(h, s, v){
    var r, g, b;

    var i = Math.floor(h * 6);
    var f = h * 6 - i;
    var p = v * (1 - s);
    var q = v * (1 - f * s);
    var t = v * (1 - (1 - f) * s);

    switch(i % 6){
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }

    return [r * 255, g * 255, b * 255];
};

/****************************************************************************/
var rgb, r, g, b, i;
var hsv, h, s, v;


var IRColorCache = {};
for(var t=0; t<=255; t++){
    h = 0;
    s = 100;
    v = 100;

    i = t / 2 - 90;
    if(t > 240){
        IRColorCache[t] = [0, 0, 0];
        continue;
    };

    if(i <= -80){
        h = 36 + 2.4 * (i + 90);
        s = 85 + 1.5 * (i + 90);
    } else if(i <= -70){
        h = 30 - 3 * (i + 80);
        s = 75 + 2.5 * (i + 80);
        v = 60 + 4 * (i + 80);
    } else if(i < -50){
        h = 120 - 1.5 * (i + 70);
        s = 100;
        v = 60 + 2 * (i + 70);
    } else if(i < -30){
        h = 240 - 2.5 * (i + 50);
        s = 100;
        v = 70 + 1.5 * (i + 50);
    } else if(i < 30){
        h = 0;
        s = 0;
        v = 100 - 100 * (i + 30) / 60;
    };

    h /= 360;
    s /= 100;
    v /= 100;

    rgb = hsvToRgb(h, s, v);
    IRColorCache[t] = [round(rgb[0]), round(rgb[1]), round(rgb[2])];
};

var IRWVCache = {};
for(var t=0; t<=255; t++){
    h = 0;
    s = 0;
    v = 100;

    i = t / 2 - 90;
    if(i < -70) i = -70;
    if(i > 0) i = 0;

    if(i <= -60){
        h = 2.4 * (i + 70);
        s = 100;
        v = 50 + 3.5 * (i + 70);
    } else if(i <= -50){
        h = 24 + 1.2 * (i + 60);
        s = 100 - 2.5 * (i + 60);
        v = 85 + 1.5 * (i + 60);
    } else if(i <= -40){
        h = 36 + 4.4 * (i + 50);
        s = 75 - 2.5 * (i + 50);
    } else if(i <= -30){
        h = 80 + 8 * (i + 40);
        s = 50;
    } else if(i <= -20){
        h = 160 + 4 * (i + 30);
        s = 50 + 3 * (i + 30);
    } else if(i <= -10){
        h = 200 + 2 * (i + 20);
        s = 80 + 0.5 * (i + 20);
        v = 100 - 1.5 * (i + 20);
    } else if(i <= 0){
        h = 220 + 8 * (i + 10);
        s = 85 + 1.5 * (i + 10);
        v = 85 - 3.5 * (i + 10);
    };
    h /= 360;
    s /= 100;
    v /= 100;

    rgb = hsvToRgb(h, s, v);
    IRWVCache[t] = [round(rgb[0]), round(rgb[1]), round(rgb[2])];
};

/****************************************************************************/

ret["IR-COLOR"] = function(data){
    var r,g,b, got;
    for(var i=0; i<data.length; i+=4){
        r = data[i];
        g = data[i+1];
        b = data[i+2];
        
        got = IRColorCache[Math.round((r+g+b) / 3)];
        
        data[i] = got[0];
        data[i+1] = got[1]; 
        data[i+2] = got[2];
    };
};

ret['IR-WV'] = function(data){
    var r,g,b, got;
    for(var i=0; i<data.length; i+=4){
        r = data[i];
        g = data[i+1];
        b = data[i+2];
        
        got = IRWVCache[Math.round((r+g+b) / 3)];
        
        data[i] = got[0];
        data[i+1] = got[1]; 
        data[i+2] = got[2];
    };
};

ret['GREY'] = function(data){
    for(var i=0; i<data.length; i+=4){
        data[i] = 255 - data[i];
        data[i+1] = 255 - data[i+1]; 
        data[i+2] = 255 - data[i+2];
    };
};



return ret;

//////////////////////////////////////////////////////////////////////////////
});
