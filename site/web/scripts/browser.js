require([
    'jquery',
    'map',
], function(
    $,
    map
){
//////////////////////////////////////////////////////////////////////////////


var mapView = new map('map');

$.get('/data/index.txt', function(txt){
    var list = txt.split('\n'), l = [];
    for(var i=0; i<list.length; i++){
        list[i] = list[i].trim();
        if('' != list[i] && 'index.txt' != list[i]) l.push(list[i]);
    };
    mapView.assignList(l);
});

//////////////////////////////////////////////////////////////////////////////
});
