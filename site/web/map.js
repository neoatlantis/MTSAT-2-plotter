mapView = {};
$(function(){
//////////////////////////////////////////////////////////////////////////////

mapView.load = function(){};




var mapBounds = L.latLngBounds(
    L.latLng(-60.02, 85.02),
    L.latLng(59.98, 360-154.98)
);
var map = L.map('map', {
    maxBounds: mapBounds,
    crs: L.CRS.EPSG4326,
}).setView([20.00, 140.00], 4);

var tileURL = "http://{s}.tile.osm.org/{z}/{x}/{y}.png";
tileURL = "http://localhost:4001/201411300032.IR1.FULL.png-split/{z}/{x}/{y}.jpg";
/*
http://{s}.tile.osm.org/{z}/{x}/{y}.png
*/
L.tileLayer(tileURL, {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 6,
    minZoom: 4,
}).addTo(map);

for(var lat=-60; lat<=60; lat+=10)
    L.circle(L.latLng(lat, 100.0), 100000).addTo(map);


//////////////////////////////////////////////////////////////////////////////
});
