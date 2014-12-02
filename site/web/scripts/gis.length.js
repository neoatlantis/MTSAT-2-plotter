/*
 * Calculate the length represented by a Polyline
 * ==============================================
 */

define(['leaflet'], function(L){
//////////////////////////////////////////////////////////////////////////////

function distance(p1, p2){
    return p1.distanceTo(p2);
};


function getGeoJSONLength(geoJSON){
    if('LineString' != geoJSON.type) return 0;
    var coords = geoJSON.coordinates;
    if(coords.length < 2) return 0;
    var last = coords[0], distanceSum = 0;
    for(var i=1; i<coords.length; i++){
        distanceSum += distance(
            L.latLng(last[0], last[1]),
            L.latLng(coords[i][0], coords[i][1])
        );
        last = coords[i];
    };
    return distanceSum;
};

return getGeoJSONLength;
//////////////////////////////////////////////////////////////////////////////
});
