mapView = {};
$(function(){
//////////////////////////////////////////////////////////////////////////////
var outCanvas = $('#imgOutput')[0],
    cropCacheCanvas = $('#imgCropCache')[0];

var initialized = false;

var image, metadata;
var zoomCoeff;
var zoomLevel = 1;  // <length in view> * zoomLevel * k -> <length in original map>
var center = {x:0, y:0}; // the center of viewer on original map.

var viewH = 600, viewW = 0;
var cropL, cropT, cropW, cropH, cropR, cropB;

mapView.updateCropRegion = function(){
    var srcW = Math.abs(metadata.range.x2 - metadata.range.x1),
        srcH = Math.abs(metadata.range.y2 - metadata.range.y1),
        srcL = Math.min(metadata.range.x2, metadata.range.x1),
        srcT = Math.min(metadata.range.y2, metadata.range.y1),
        srcR = srcW + srcL,
        srcB = srcH + srcT;
    viewW = Math.floor(srcW / srcH * viewH);

    zoomCoeff = srcW / (viewW * zoomLevel);
    if(zoomCoeff < 1){
        zoomCoeff = 1;
        zoomLevel = Math.floor(srcW / viewW);
        if(zoomLevel < 1) zoomLevel = 1;
    };

    cropW = viewW * zoomCoeff;
    cropH = viewH * zoomCoeff;
    cropL = center.x - cropW / 2;
    cropT = center.y - cropH / 2;
    cropR = cropL + cropW;
    cropB = cropT + cropH;

    if(cropL < srcL){
        cropL = srcL;
        center.x = srcL + cropW / 2;
    };
    if(cropR > srcR){    
        cropL = srcR - cropW;
        center.x = srcR - cropW / 2;
    };

    if(cropT < srcT){
        cropT = srcT;
        center.y = srcT + cropH / 2;
    };
    if(cropB > srcB){    
        cropT = srcB - cropH;
        center.y = srcB - cropH / 2;
    };
};

mapView.redraw = function(){
    if(!initialized) return;

    mapView.updateCropRegion();

    // (cropL, cropT, cropW, cropH) defines the region to be cropped from the
    // original image, which will be resized into (viewW x viewH)

    outCanvasContext = outCanvas.getContext('2d');
    outCanvasContext.canvas.width = viewW;
    outCanvasContext.canvas.height = viewH;

    console.log(cropL, cropT, cropW, cropH);

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

mapView.mouseDrag = function(deltaX, deltaY){
    center.x -= deltaX * zoomCoeff;
    center.y -= deltaY * zoomCoeff;
    mapView.redraw();
};

mapView.mouseDblclick = function(clickX, clickY){
    zoomLevel += 1;
    center.x = clickX * zoomCoeff;
    center.y = clickY * zoomCoeff;
    mapView.redraw();
};

mapView.load = function(img, m){
    image = img;
    metadata = m;

    if(!initialized){
        center.x = 0.5 * (metadata.range.x2 + metadata.range.x1);
        center.y = 0.5 * (metadata.range.y2 + metadata.range.y1);
        zoomLevel = 1;

        initialized = true;
    };

    mapView.redraw();
};

$('.viewer-zoomin').click(function(){
    zoomLevel += 1;
    mapView.redraw();
});

$('.viewer-zoomout').click(function(){
    zoomLevel -= 1;
    if(zoomLevel < 1) zoomLevel = 1;
    mapView.redraw();
});


var mouseDragging = false,
    startDragging = {x:0, y:0},
    endDragging = {x:0, y:0};
$("#viewer").mousedown(function(e){
    mouseDragging = true;
    startDragging.x = e.clientX;
    startDragging.y = e.clientY;
});
$("#viewer").mouseup(function(e){
    if(mouseDragging){
        endDragging.x = e.clientX;
        endDragging.y = e.clientY;

        var deltaX = endDragging.x - startDragging.x,
            deltaY = endDragging.y - startDragging.y;
    
        mapView.mouseDrag(deltaX, deltaY);
    };
    mouseDragging = false;
});
$("#viewer").mouseleave(function(e){
    mouseDragging = false;
});
$("#viewer").dblclick(function(e){
    var offset = $(this).offset();
    mapView.mouseDblclick(
        e.clientX - offset.left,
        e.clientY - offset.top
    );
});


//////////////////////////////////////////////////////////////////////////////
});
