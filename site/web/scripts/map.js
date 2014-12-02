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
/*
http://{s}.tile.osm.org/{z}/{x}/{y}.png
*/
L.tileLayer(tileURL, {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> | ' +
        '<a href="http://www.cr.chiba-u.jp/english/">CEReS</a>, Chiba University | ' +
        '<a href="http://www.naturalearthdata.com/">Natural Earth</a>',
    maxZoom: 6,
    minZoom: 3,
}).addTo(map);


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
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

// when new area drawn
map.on('draw:created', function (e) {
    var type = e.layerType,
        layer = e.layer;

    if (type === 'polygon' || type === 'rectangle') {
        // Do marker specific actions
        map.addLayer(layer);
        
        var geoJSON = layer.toGeoJSON().geometry;
        console.log(geoJSON);
        console.log(getGeoJSONArea.geometry(geoJSON));
    }
});

//////////////////////////////////////////////////////////////////////////////
return mapView;
});
