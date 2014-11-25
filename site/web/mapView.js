mapView = {};
$(function(){
//////////////////////////////////////////////////////////////////////////////
var outCanvas = $('#imgOutput')[0],
    cropCacheCanvas = $('#imgCropCache')[0];

mapView.statusSubscribers = [];
function emitStatusChanged(){
    var v = $('.viewer-cursor-vertical'),
        h = $('.viewer-cursor-horizontal');
    var vLeft = parseInt(v.css('left')),
        vWidth = parseInt(v.css('width'));
    var hTop = parseInt(h.css('top')),
        hHeight = parseInt(h.css('height'));
    var mouseX = vLeft + vWidth / 2,
        mouseY = hTop + hHeight / 2;
    mapView.calculateCursorGreyScale(mouseX, mouseY);
    mapView.calculateCursorLatLng(mouseX, mouseY);

    for(var i=0; i<mapView.statusSubscribers.length; i++)
        mapView.statusSubscribers[i]();
};

var initialized = false;

var image, metadata;
var zoomCoeff;
var zoomLevel = 1;  // <length in view> * zoomLevel * k -> <length in original map>
var center = {x:0, y:0}; // the center of viewer on original map.

var viewH = 600, viewW = 0;
var cropL, cropT, cropW, cropH, cropR, cropB;

// TODO for VIS channel this is different
var srcLatN = 59.98, srcLngW = 85.02,
    srcPixelLat = 0.04, srcPixelLng = 0.04;
var cursorLat, cursorLng, cursorGreyScale;

mapView.updateCropRegion = function(){
    var srcW = Math.abs(metadata.range.x2 - metadata.range.x1),
        srcH = Math.abs(metadata.range.y2 - metadata.range.y1),
        srcL = Math.min(metadata.range.x2, metadata.range.x1),
        srcT = Math.min(metadata.range.y2, metadata.range.y1),
        srcR = srcW + srcL,
        srcB = srcH + srcT;
    viewW = srcW / srcH * viewH;

    if(zoomLevel < 1) zoomLevel = 1;
    zoomCoeff = srcW / (viewW * zoomLevel);
    if(zoomCoeff < 1){
        zoomCoeff = 1;
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
    
    emitStatusChanged();
};

mapView.calculateCursorLatLng = function(mouseX, mouseY){
    // viewW, viewH
    var pixelYToCenter = viewH / 2 - mouseY,
        pixelXToCenter = viewW / 2 - mouseX;

    var cursorPixelLat = center.y - pixelYToCenter * zoomCoeff,
        cursorPixelLng = center.x - pixelXToCenter * zoomCoeff;
    
    cursorLat = srcLatN - cursorPixelLat * srcPixelLat;
    cursorLng = srcLngW + cursorPixelLng * srcPixelLng;
    if(cursorLng > 180) cursorLng -= 360;
};
mapView.getCursorLatLng = function(){
    return {lat: cursorLat, lng: cursorLng};
};


// dealing with calculation from grey scale to real value
mapView.calculateCursorGreyScale = function(mouseX, mouseY){
    var outCanvasContext = outCanvas.getContext('2d');
    var data = outCanvasContext.getImageData(mouseX, mouseY, 1, 1);
    cursorGreyScale = 0.5 * (data.data[1] + data.data[2]);
    console.log(cursorGreyScale)
};
mapView.getCursorValue = function(){
    var scaleMax = metadata.scale.max,
        scaleMin = metadata.scale.min,
        inverted = metadata.scale.inverted;
    var sv = cursorGreyScale;
    if(inverted) sv = 255 - sv;
    return scaleMin + (sv / 255) * (scaleMax - scaleMin);
};
mapView.getCursorValueUnit = function(){
    return metadata.scale.unit;
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
        emitStatusChanged();
    };
    mouseDragging = false;
});
$("#viewer").mouseleave(function(e){
    mouseDragging = false;
});



/* define behaviours of draggable crosshair */
var crosshairHDragging = false, crosshairVDragging = false,
    crosshairHDragStart = 0, crosshairVDragStart = 0;
$('.viewer-cursor-horizontal')
    .mousedown(function(e){
        e.stopPropagation();
        crosshairHDragging = true;
        crosshairHDragStart = e.clientY;
    })
    .mousemove(function(e){
        e.stopPropagation();
        if(!crosshairHDragging) return;
        $(this).css('top', "+=" + String(e.clientY - crosshairHDragStart));
        crosshairHDragStart = e.clientY;
        emitStatusChanged();
    })
    .on('mouseup mouseleave', function(e){
        e.stopPropagation();
        crosshairHDragging = false;
    })
;
$('.viewer-cursor-vertical')
    .mousedown(function(e){
        e.stopPropagation();
        crosshairVDragging = true;
        crosshairVDragStart = e.clientX;
    })
    .mousemove(function(e){
        e.stopPropagation();
        if(!crosshairVDragging) return;
        $(this).css('left', "+=" + String(e.clientX - crosshairVDragStart));
        crosshairVDragStart = e.clientX;
        emitStatusChanged();
    })
    .on('mouseup mouseleave', function(e){
        e.stopPropagation();
        crosshairVDragging = false;
    })
;


//////////////////////////////////////////////////////////////////////////////
});
