require([
    'jquery',
    'leaflet',
    'gis.area',

    'leaflet.mouseposition',
    'leaflet.draw',
], function(
    $,
    L,
    getGeoJSONArea
){

var mapView = {};
//////////////////////////////////////////////////////////////////////////////

mapView.load = function(){};




var mapBounds = L.latLngBounds(
    L.latLng(-60.02, 85.02),
    L.latLng(58.98, 360-154.98)
);
var map = L.map('map', {
    maxBounds: mapBounds,
    crs: L.CRS.EPSG4326,
}).setView([20.00, 140.00], 4);

L.control.mousePosition({
    prefix: '鼠标位置:',
    separator: ' / ',
    emptyString: '在地图上移动鼠标以获取位置',

}).addTo(map);

var tileURL = "http://{s}.tile.osm.org/{z}/{x}/{y}.png";
tileURL = "http://localhost:4001/201411300032.IR1.FULL.png-split/{z}/{x}/{y}.png";


var canvasTiles = L.tileLayer.canvas({
    maxZoom: 6,
    minZoom: 3,
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> | ' +
        '<a href="http://www.cr.chiba-u.jp/english/">CEReS</a>, Chiba University | ' +
        '<a href="http://www.naturalearthdata.com/">Natural Earth</a>',
});
canvasTiles.drawTile = function(canvas, tilePoint, zoom){
    var countMax = 1 << zoom;
    var ctx = canvas.getContext('2d');
    // draw something on the tile canvas
    var img = new Image();
    img.src = "http://localhost:4001/201411300032.IR1.FULL.png-split/" + zoom + "/" + (tilePoint.x % countMax) + "/" + (tilePoint.y % countMax) + ".png"
    img.onload = function(){
        ctx.drawImage(img, 0, 0, 256, 256);
    };
};
canvasTiles.addTo(map);



$.getJSON('./static/geojson/coastline.json', function(json){
    L.geoJson(json, {
        style: {
            'weight': '1.5px',
            'color': '#FFAA00',
            'opacity': '1.0',
        },
    }).addTo(map);
});

$.getJSON('./static/geojson/graticules.json', function(json){
    L.geoJson(json, {
        style: {
            'weight': '1.5px',
            'color': '#FFAA00',
            'opacity': '1.0',
        },
    }).addTo(map);
});

$.getJSON('./static/geojson/boundaries.json', function(json){
    L.geoJson(json, {
        style: {
            'weight': '1.5px',
            'color': '#FF0000',
            'opacity': '1.0',
        },
    }).addTo(map);
});


/* initialize the drawing toolbar */

// Initialise the FeatureGroup to store editable layers
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Initialise the draw control and pass it the FeatureGroup of editable layers
var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
        remove: true,
        edit: true,
    },
    draw: {
        polygon: {
            allowIntersection: false, // Restricts shapes to simple polygons
            drawError: {
                color: '#FF0000', // Color the shape will turn when intersects
                message: '<strong>错误！<strong>不能绘制相交线。' // Message that will show when intersect
            },
            shapeOptions: {
                color: '#FF00FF',
            },
        },
        rectangle: {
            shapeOptions: {
                color: '#FF00FF',
            },
        },
        polyline: false,
        marker: false,
        circle: false,
    },
});
map.addControl(drawControl);


function bindPopupToLayer(layer){
    var geoJSON = layer.toGeoJSON().geometry;
    var area = (getGeoJSONArea.geometry(geoJSON) / 1000000);
    layer.bindPopup('<strong>面积：</strong>' + String(L.Util.formatNum(area, 2)) + ' km&sup2;');
}

// when new area drawn
map.on('draw:created', function(e) {
    var type = e.layerType,
        layer = e.layer;
    if ('polygon' != type && 'rectangle' != type) return;
    bindPopupToLayer(layer);
    drawnItems.addLayer(layer);
});

// when area edited
map.on('draw:edited', function(e){
    e.layers.eachLayer(bindPopupToLayer);
});

// mouseevent
map.on('mousemove', function(e){
});

//////////////////////////////////////////////////////////////////////////////
return mapView;
});
