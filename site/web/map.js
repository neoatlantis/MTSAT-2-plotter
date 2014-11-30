mapView = {};
$(function(){
//////////////////////////////////////////////////////////////////////////////

mapView.load = function(){};




var mapBounds = L.latLngBounds(
    L.latLng(-60.02, 85.02),
    L.latLng(59.98, -154.98)
);
var map = L.map('map', {
    maxBounds: mapBounds,
}).setView([20.00, 140.00], 4);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 6,
    minZoom: 2,
}).addTo(map);


//////////////////////////////////////////////////////////////////////////////
});
