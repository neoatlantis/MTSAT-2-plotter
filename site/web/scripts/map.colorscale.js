define([], function(){
//////////////////////////////////////////////////////////////////////////////

var ret = {};

function round(color){
    var r = Math.round(color);
    if(r > 255) r = 255;
    if(r < 0) r = 0;
    return r;
};

var r,g,b, i;
var IRColorCache = {};
for(var t=0; t<=255; t++){
    if(t > 240){
        IRColorCache[t] = [0, 0, 0];
        continue;
    };

    r = 0; g = 0; b = 0;
    i = t / 2 - 90;
    if(i <= -80){
        r = 255;
        g = 127 + (i + 90) * 12.7;
    } else if (i <= -70){
        r = 127 + (i + 80) * 12.7;
    } else if(i <= -50){
        g = 155 + (i + 70) * 5;
    } else if(i <= -30){
        b = 255;
        g = (i + 50) * 12.75;
    } else if(i <= 30){
        r = 255 - (i + 30) * 4.25;
        g = r;
        b = r;
    };
    IRColorCache[t] = [round(r), round(g), round(b)];
};
console.log(IRColorCache)

/****************************************************************************/

ret["IR-COLOR"] = function(data){
    var r,g,b, Tbb, got;
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



return ret;

//////////////////////////////////////////////////////////////////////////////
});
