mapView = {};
$(function(){
//////////////////////////////////////////////////////////////////////////////
var outCanvas = $('#imgOutput')[0],
    cropCacheCanvas = $('#imgCropCache')[0];

var image, metadata;
var zoomLevel = 1;  // <length in view> * zoomLevel * k -> <length in original map>
var center = {x:0, y:0}; // the center of viewer on original map.

var viewH = 600, viewW = 0;

mapView.redraw = function(){
    var srcW = Math.abs(metadata.range.x2 - metadata.range.x1),
        srcH = Math.abs(metadata.range.y2 - metadata.range.y1),
        srcL = Math.min(metadata.range.x2, metadata.range.x1),
        srcT = Math.min(metadata.range.y2, metadata.range.y1);
    viewW = Math.floor(srcW / srcH * viewH);

    var zoomCoeff = srcW / (viewW * zoomLevel);
    if(zoomCoeff < 1) zoomCoeff = 1;

    var cropW = viewW * zoomCoeff,
        cropH = viewH * zoomCoeff,
        cropL = center.x - cropW / 2,
        cropT = center.y - cropH / 2;
    if(cropL < 0){
        cropL = 0;
        center.x = cropW / 2;
    };
    if(cropL > srcL + srcW){    
        cropL = srcL + srcW - cropW;
        center.x = srcL + srcW - cropW / 2;
    };
    if(cropT < 0){
        cropT = 0;
        center.y = cropH / 2;
    };
    if(cropT > srcT + srcH){    
        cropT = srcT + srcH - cropH;
        center.y = srcT + srcH - cropH / 2;
    };

    // (cropL, cropT, cropW, cropH) defines the region to be cropped from the
    // original image, which will be resized into (viewW x viewH)

    outCanvasContext = outCanvas.getContext('2d');
    outCanvasContext.canvas.width = viewW;
    outCanvasContext.canvas.height = viewH;

    outCanvasContext.drawImage(
        image,
        cropL,
        cropT,
        cropW,
        cropH,
        0,
        0,
        viewW,
        viewH
    );
    
};

mapView.load = function(img, m){
    image = img;
    metadata = m;

    center.x = 0.5 * (metadata.range.x2 + metadata.range.x1);
    center.y = 0.5 * (metadata.range.y2 + metadata.range.y1);
    zoomLevel = 1;

    mapView.redraw();
};

//////////////////////////////////////////////////////////////////////////////
});
