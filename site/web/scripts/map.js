require([
    'jquery',
    'leaflet',
    'gis.area',
    'gis.length',

    'leaflet.mouseposition',
    'leaflet.draw',
    'leaflet.button',
], function(
    $,
    L,
    getGeoJSONArea,
    getGeoJSONLength
){
//////////////////////////////////////////////////////////////////////////////

/* define some utilities */
function floatToDegree(f, latLng='lat'){
    function twoDigits(x){return ((x>10)?String(x):'0' + String(x));};
    var str = '', negative=false;
    if('lat' == latLng){
        if(0 == f) return '赤道';
        negative = (f < 0);
        if(negative) f = Math.abs(f);
        f = f % 90;
    } else {
        if(0 == f) return '0&deg;';
        negative = (f < 0) || (f > 180);
        if(f > 180) f = f - 360;
        if(negative) f = Math.abs(f);
        f = f % 180;
    };
    
    var m = Math.floor(f);
    str += m + '&deg;';
    
    f -= m;
    f *= 60;
    
    m = Math.floor(f);
    str += twoDigits(m) + "'";

    f -= m;
    f *= 60;

    m = Math.floor(f);
    str += twoDigits(m) + '"';

    str += ' ';
    if('lat' == latLng)
        str += (negative?'S':'N');
    else
        str += (negative?'W':'E');
    return str;
};

/****************************************************************************/

function mapView(divID){
    var self = this;

    // create div for map region
    $('#' + divID)
        .empty()
        .append(
            $('<div>', {id: divID + '-leaflet'})
        )
        .append(
            $('<div>', {id: divID + '-status'}).addClass('map-status')
        )
        .append(
            $('<div>', {id: divID + '-menu'}).addClass('map-menu').hide()
        )
    ;

    // auto resize adjustment
    function autoResizeAdjustment(){
        $('#' + divID + '-leaflet')
            .css('height', ($(window).height() - 32) + 'px')
        ;
    };
    $(window).resize(autoResizeAdjustment);
    $(document).resize(autoResizeAdjustment);
    autoResizeAdjustment();


    // define map zoom range
    var mapZoomMax = 6,
        mapZoomMin = 4;

    // define map bounds
    var mapBounds = L.latLngBounds(
        L.latLng(-60.02, 85.02),
        L.latLng(58.98, 360-154.98)
    );

    // define map attribution
    var mapAttribution = 
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> | ' +
        '<a href="http://www.cr.chiba-u.jp/english/">CEReS</a>, Chiba University | ' +
        '<a href="http://www.naturalearthdata.com/">Natural Earth</a>'
    ;

    // initialize the map instance
    var map = L.map(divID + '-leaflet', {
        maxBounds: mapBounds,
        crs: L.CRS.EPSG4326,
    }).setView(mapBounds.getCenter(), mapZoomMin);

    
    // add mouse position displayer to map
    
    L.control.mousePosition({
        prefix: '鼠标位置:',
        separator: ' / ',
        emptyString: '在地图上移动鼠标以获取位置',
        lngFormatter: function(x){return floatToDegree(x, 'lng')},
        latFormatter: function(x){return floatToDegree(x, 'lat')},
    }).addTo(map);


    // geoJSON layer toggler
    var geoJSONLayers = {}, geoJSONLayersVisibility = {};
    function toggleGeoJSON(name, displayStyle){
        geoJSONLayersVisibility[name] = !Boolean(geoJSONLayersVisibility[name]);
        if(null == geoJSONLayers[name]){
            $.getJSON('./static/geojson/' + name + '.json', function(json){
                var geoJSON = L.geoJson(json, {
                    style: displayStyle
                })
                geoJSONLayers[name] = geoJSON;
                if(geoJSONLayersVisibility[name])
                    geoJSONLayers[name].addTo(map);
            });
        } else {
            if(geoJSONLayersVisibility[name])
                geoJSONLayers[name].addTo(map);
            else
                map.removeLayer(geoJSONLayers[name]);
        };
        return geoJSONLayersVisibility[name];
    };

    // status displayer outside the map
    var statusList = [
        'dragging',
        'graticules',
        'regionlines',
        'datetime',
    ];
    function showStatus(name, value){
        var parentSelector = '#' + divID + '-status',
            selector = parentSelector + ' [name="' + name + '"]';
        if($(selector).length < 1){
            $(parentSelector).append(
                $('<div>', {name: name})
                    .addClass('map-status-box')
            );
        };
        if(undefined === value) return $(selector);

        var text = '';
        if('dragging' == name){
            text += '鼠标拖动';
        } else if('graticules' == name){
            text += '经纬网';
        } else if('regionlines' == name){
            text += '地区边界';
        } else if('datetime' == name){
            text += new Date(value).toUTCString();
            value = text;
        } else
            text = value;

        if(true === value)
            $(selector).removeClass('map-status-disabled');
        else if(false === value)
            $(selector).addClass('map-status-disabled');

        $(selector).text(text);
    };
    for(var i=0; i<statusList.length; i++) showStatus(statusList[i], false);

    /********************************************************************/
    /* Internal functions for controlling map */

    var mapDraggingStatus = null;
    function mapDraggingEnabled(v){
        mapDraggingStatus = v;
        showStatus('dragging', v);
        if(v)
            map.dragging.enable();
        else
            map.dragging.disable();
    };
    mapDraggingEnabled(true);


    /********************************************************************/
    /* add drawing and measuring abilities to the map */

    // Initialise the FeatureGroup to store editable layers
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var crosshairIcon = L.Icon.extend({
        options: {
            shadowUrl: null,
            iconAnchor: new L.Point(16, 16),
            iconSize: new L.Point(32, 32),
            iconUrl: './static/images/crosshair.png'
        }
    });

    // Initialise the draw control and pass it the FeatureGroup of editable
    // layers
    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems,
            remove: true,
            edit: true,
        },
        draw: {
            polygon: {
                allowIntersection: false,
                drawError: {
                    color: '#FF0000',
                    message: '<strong>错误！<strong>不能绘制相交线。'
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
            marker: {
                icon: new crosshairIcon(),
            },
            polyline: {
                shapeOptions: {
                    color: '#FF00FF',
                    weight: '4px',
                },
            },
            circle: false,
        },
    });
    map.addControl(drawControl);


    function bindPopupToLayer(layer){
        var geoJSON = layer.toGeoJSON().geometry;
        var type = layer.type;
        if ('polygon' == type || 'rectangle' == type){
            var area = (getGeoJSONArea.geometry(geoJSON) / 1000000);
            layer.bindPopup(
                '<strong>面积：</strong>' + 
                String(L.Util.formatNum(area, 2)) + 
                ' km&sup2;'
            );
        } else if('marker' == type){
            layer.bindPopup(
                '<strong>纬度</strong> ' +
                floatToDegree(layer._latlng.lat, 'lat') +
                '<br />' +
                '<strong>经度</strong> ' +
                floatToDegree(layer._latlng.lng, 'lng')
            );
        } else if('polyline' == type){
            var len = (getGeoJSONLength(geoJSON) / 1000);
            layer.bindPopup(
                '<strong>长度：</strong>' + 
                String(L.Util.formatNum(len)) +
                ' km'
            );
        };
    }

    // when new area drawn
    map.on('draw:created', function(e) {
        var type = e.layerType,
            layer = e.layer;
        layer.type = e.layerType
        bindPopupToLayer(layer);
        drawnItems.addLayer(layer);
    });

    // when area edited
    map.on('draw:edited', function(e){
        e.layers.eachLayer(bindPopupToLayer);
    });

    // when draw begins, stop dragging
    map.on('draw:drawstart', function(){
        mapDraggingEnabled(false);
    })

    // when draw ends, resume dragging
    map.on('draw:drawstop', function(){
        mapDraggingEnabled(true);
    });

    // mouseevent
    map.on('mousemove', function(e){
    });



    /********************************************************************/
    /* now the methods being exposed */


    // show or hide a cloud atlas with given name
    // - when `name` is not specified, will hide all drawn altases.
    // - otherwise, the layer with given name will be shown, while the others
    //   being hide.

    var cloudAtlasLayers = {};
    this.toggleCloudAtlas = function(name){
        if(!name){
            for(var i in cloudAtlasLayers)
                map.removeLayer(cloudAtlasLayers[i]);
            return;
        };

        if(undefined == cloudAtlasLayers[name]){
            var tileURL = "/{name}/{z}/{x}/{y}.{f}";
            var canvasTiles = L.tileLayer.canvas({
                maxZoom: mapZoomMax,
                minZoom: mapZoomMin,
                attribution: mapAttribution,
            });
            canvasTiles.drawTile = function(canvas, tilePoint, zoom){
                var countMax = 1 << zoom;
                var ctx = canvas.getContext('2d');
                // draw something on the tile canvas

                var img = new Image();
                var imgFormat = ((zoom <= 5)?'jpg':'png');
                var url = tileURL
                    .replace('{name}', name)
                    .replace('{z}', String(zoom))
                    .replace('{x}', String(tilePoint.x % countMax))
                    .replace('{y}', String(tilePoint.y % countMax))
                    .replace('{f}', imgFormat)
                ;
                img.src = url; 
                img.onload = function(){
                    ctx.drawImage(img, 0, 0, 256, 256);
                };
            };
            cloudAtlasLayers[name] = canvasTiles;
        } else {
            var canvasTiles = cloudAtlasLayers[name];
        };

        for(var i in cloudAtlasLayers){
            if(i == name)
                cloudAtlasLayers[i].addTo(map);
            else
                map.removeLayer(cloudAtlasLayers[i]);
        };
        return self;
    };


    // show or hide region lines
    
    this.toggleRegionLines = function(){
        var s1 = toggleGeoJSON('coastline', {
            'weight': '1.5px',
            'color': '#FFAA00',
            'opacity': '0.5',
        });
        var s2 = toggleGeoJSON('boundaries', {
            'weight': '1.5px',
            'color': '#FF0000',
            'opacity': '0.5',
        });
        showStatus('regionlines', s1 || s2);
        return self;
    };

    // show or hide graticules

    this.toggleGraticules = function(){
        var s = toggleGeoJSON('graticules', {
            'weight': '1.5px',
            'color': '#FFAA00',
            'opacity': '1.0',
        });
        showStatus('graticules', s);
        return self;
    };


    // enable or disable mouse map dragging
    self.toggleMapDragging = function(){
        mapDraggingEnabled(!mapDraggingStatus);
    };


    // show or hide menu for selecting layer
    self.toggleMenu = function(){
        $('#' + divID + '-menu')
            .toggle()
//            .css('bottom', $('#' + divID + '-status').css('height'))
//            .css('right', '0px')
        ;
    };


    // bind mouse events to status bars
    showStatus('dragging').addClass('map-status-not-link');
    showStatus('datetime').click(self.toggleMenu);
    showStatus('graticules').click(self.toggleGraticules);
    showStatus('regionlines').click(self.toggleRegionLines);

    return this;
};






var mapViewInstance = new mapView('map');

mapViewInstance
    .toggleCloudAtlas('201411300032.IR1.FULL.png-split')
    .toggleCloudAtlas('201301150132.IR1.FULL.png-split')
    .toggleRegionLines()
;

//////////////////////////////////////////////////////////////////////////////
return mapViewInstance;
});
