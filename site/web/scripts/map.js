define([
    'jquery',
    'leaflet',
    'gis.area',
    'gis.length',
    'map.colorscale',

    'leaflet.mouseposition',
    'leaflet.draw',
    'tooltip',
], function(
    $,
    L,
    getGeoJSONArea,
    getGeoJSONLength,
    colorscale
){
//////////////////////////////////////////////////////////////////////////////

/* define some utilities */
function floatToDegree(f, latLng){
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

function date12ToStr(d12){
    return String(
        d12.slice(0,4) + '年' + 
        d12.slice(4,6) + '月' +
        d12.slice(6,8) + '日' +
        ' ' +
        d12.slice(8,10) + ':' +
        d12.slice(10,12) +
        ' UTC'
    );
};

/****************************************************************************/

function mapView(divID){
    var self = this;

    var dataChannelList = ['IR1', 'IR2', 'IR3'],
        dataChannel = 0,
        dataDateList = [],
        dataDate = 0,
        dataRegion = 0, // 0-full, 1-inc. North, 2-inc. South
        dataFileName = {};

    var dataColorify = {
        'IR1': {
            methods: ['IR-GREY', 'IR-COLOR', 'IR-BD', 'IR-BD-COLOR'],
            pointer: 0,
        },
        'IR2': {
            methods: ['IR-GREY', 'IR-COLOR', 'IR-BD', 'IR-BD-COLOR'],
            pointer: 0,
        },
        'IR3': {
            methods: ['IR-GREY', 'IR-WV'],
            pointer: 0,
        },
        'VIS': {
            methods: ['VIS-GREY'],
            pointer: 0,
        },
    };

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
        .append(
            $('<div>', {id: divID + '-colorscale'})
                .addClass('map-colorscale')
                .hide()
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
        '<a href="http://www.cr.chiba-u.jp/english/" target="_blank">CEReS</a>, Chiba University | ' +
        '<a href="http://www.naturalearthdata.com/" target="_blank">Natural Earth</a> || ' +
        '<a href="http://neoatlantis.org/mtsat-2.html" target="_blank">使用条款和说明</a>'
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
                    style: displayStyle,
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
        'colorify',
        'channel',
        'region',
        'datetime',
    ];
    function showStatus(name, value){
        var parentSelector = '#' + divID + '-status',
            selector = parentSelector + ' [name="' + name + '"]';

        if($(selector).length < 1 && statusList.indexOf(name) >= 0){
            if('datetime' == name){
                $('<div>')
                    .append(
                        $('<span>', {name: 'datetime-prev'}).html('&#9664; ')
                    )
                    .append(
                        $('<span>', {name: 'datetime'})
                    )
                    .append(
                        $('<span>', {name: 'datetime-next'}).html(' &#9654;')
                    )
                .addClass('map-status-box')
                .appendTo(parentSelector);
            } else
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
            text += value;
            value = null;
        } else if('channel' == name){
            text += '通道 ' + dataChannelList[dataChannel];
            value = null;
        } else if('region' == name){
            text += '范围 '
            if(1 == dataRegion)
                text += '北半球';
            else if(2 == dataRegion)
                text += '南半球';
            else
                text += '全部';
            value = null;
        } else if('colorify' == name){
            var channelName = dataChannelList[dataChannel];
            text += colorscale[
                dataColorify[channelName].methods[
                    dataColorify[channelName].pointer
                ]
            ].name;
            value = null;
        } else
            text = value;

        if(true === value)
            $(selector).removeClass('map-status-disabled');
        else if(false === value)
            $(selector).addClass('map-status-disabled');

        $(selector).html(text);
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
    function updateColorScale(newCloudAtlasDrawn){
        var channelName = dataChannelList[dataChannel];
        var colorscaleName = dataColorify[channelName].methods[
                dataColorify[channelName].pointer
            ],
            colorscaleFunc = colorscale[colorscaleName].func,
            labelFunc = colorscale[colorscaleName].convertGrayscale
        ;
        var container = $('.map-colorscale');
        if(!newCloudAtlasDrawn) return container.hide();
        container.show();

        if(!container.data('initialized')){
            container.empty();
            for(var i=0; i<=240; i+=2){
                var elementID = 'map-colorscale-line-' + i;
                var element = $('<div>', {id: elementID})
                    .appendTo(container)
                    .addClass('map-colorscale-line')
                    .data('grayscale', i)
                    .data('opentip', new Opentip('#' + elementID, {
                        target: '#' + elementID,
                        tipJoint: 'right',
                        group: 'colorscale',
                        delay: 0,
                        hideDelay: 0,
                    }))
                ;
            };
            container.data('initialized', true);
        };

        container.find('.map-colorscale-line').each(function(){
            var i = $(this).data('grayscale');
            var color = [i,i,i,0];
            colorscaleFunc(color);
            $(this)
                .css(
                    'background-color', 
                    'rgb(' + color.slice(0,3).join(',') + ')'
                )
            ;
            $(this).data('opentip').setContent(labelFunc(i));
        });
    };
    this.toggleCloudAtlas = function(d12){
        var filename = dataFileName[d12], 
            channel = dataChannelList[dataChannel];

        if(filename){
            filename = filename[channel];
            if(!filename)
                filename = false;
        };

        if(!d12 || !filename){
            for(var i in cloudAtlasLayers)
                map.removeLayer(cloudAtlasLayers[i]);
            updateColorScale(false);
            return;
        };

        if(undefined == cloudAtlasLayers[filename]){
            var tileURL = "/data/{name}/{z}/{x}/{y}.{f}";
            var canvasTiles = L.tileLayer.canvas({
                maxZoom: mapZoomMax,
                minZoom: mapZoomMin,
                attribution: mapAttribution,
            });
            canvasTiles.drawTile = function(canvas, tilePoint, zoom){
                var countMax = 1 << zoom;
                var channelName = dataChannelList[dataChannel];
                var ctx = canvas.getContext('2d');
                // draw something on the tile canvas

                var img = new Image();
                var imgFormat = ((zoom <= 5)?'jpg':'png');
                var url = tileURL
                    .replace('{name}', filename)
                    .replace('{z}', String(zoom))
                    .replace('{x}', String(tilePoint.x % countMax))
                    .replace('{y}', String(tilePoint.y % countMax))
                    .replace('{f}', imgFormat)
                ;
                var colorscaleName = dataColorify[channelName].methods[
                        dataColorify[channelName].pointer
                    ],
                    colorscaleFunc = colorscale[colorscaleName].func
                ;
                    
                img.src = url; 
                img.onload = function(){
                    ctx.drawImage(img, 0, 0, 256, 256);
                    var imgdata = ctx.getImageData(0, 0, 256, 256);
                    colorscaleFunc(imgdata.data);
                    ctx.putImageData(imgdata, 0, 0);
                };
            };
            cloudAtlasLayers[filename] = canvasTiles;
        } else {
            var canvasTiles = cloudAtlasLayers[filename];
        };

        var newCloudAtlasDrawn = false;
        for(var i in cloudAtlasLayers){
            if(i == filename){
                cloudAtlasLayers[i].addTo(map);
                newCloudAtlasDrawn = true;
            } else
                map.removeLayer(cloudAtlasLayers[i]);
        };
        updateColorScale(newCloudAtlasDrawn);
        return self;
    };


    // show or hide region lines
    
    this.toggleRegionLines = function(){
        var s1 = toggleGeoJSON('coastline', {
            'weight': '1.5px',
            'color': '#FF0000',
            'opacity': '0.8',
        });
        var s2 = toggleGeoJSON('boundaries', {
            'weight': '1.5px',
            'color': '#FF0000',
            'opacity': '0.8',
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

    // enable or disable colorify
    self.toggleColorify = function(){
        var channelName = dataChannelList[dataChannel];
        var pointer = dataColorify[channelName].pointer;
        var methods = dataColorify[channelName].methods;
        pointer++;
        if(pointer > methods.length - 1) pointer = 0;
        dataColorify[channelName].pointer = pointer;
        showStatus('colorify', 'useless-value-for-updating');
        clearCloudAtlasCache();
        updateCloudAtlas();
    };


    // show or hide menu for selecting layer
    var menuStatus = false;
    self.toggleMenu = function(forceStatus){
        var target = $('#' + divID + '-menu');
        if(true === forceStatus){
            menuStatus = true;
            target.show();
        } else if(false === forceStatus){
            menuStatus = false;
            target.hide();
        } else {
            menuStatus = !menuStatus;
            if(menuStatus)
                target.show();
            else
                target.hide();
        };
        $('.map-menu-item').click();
        return menuStatus;
    };

    // bind mouse events to status bars
    showStatus('dragging').addClass('map-status-not-link');
    showStatus('graticules').click(self.toggleGraticules);
    showStatus('regionlines').click(self.toggleRegionLines);
    showStatus('colorify').click(self.toggleColorify);

    
    /********************************************************************/
    /* Data Source assign and navigation */

    function updateCloudAtlas(){
        if(dataDate >= dataDateList.length) dataDate = 0;
        if(dataDate < 0) dataDate = dataDateList.length - 1;
        if(dataDateList.length < 1){
            showStatus('datetime', '单击选取图像列表');
            self.toggleCloudAtlas(false);
        } else {
            self.toggleCloudAtlas(dataDateList[dataDate]);
            showStatus('datetime', date12ToStr(dataDateList[dataDate]));
        };
    };

    function clearCloudAtlasCache(){
        self.toggleCloudAtlas(false);
    };

    $('#' + divID + '-menu').click(function(e){
        e.stopPropagation();
    });
    showStatus('datetime').click(function(e){
        self.toggleMenu();
        menuListChanged();
        e.stopPropagation();
    });
    showStatus('datetime-next').click(function(){
        dataDate += 1;
        updateCloudAtlas();
    });
    showStatus('datetime-prev').click(function(){
        dataDate -= 1;
        updateCloudAtlas();
    });
    
    showStatus('channel').click(function(){
        dataChannel = (dataChannel + 1) % dataChannelList.length;
        showStatus('channel', dataChannel);
        showStatus('colorify', 'useless-value-for-updating');
        updateCloudAtlas();
    });

    showStatus('region').click(function(){
        dataRegion += 1;
        if(dataRegion > 2) dataRegion = 0;
        if(dataRegion < 0) dataRegion = 2;
        showStatus('region', dataRegion);
        menuListFilter();
    });

    self.assignList = function(list){
        var menuDiv = $('#' + divID + '-menu').empty();
        var dateStrList = [], regionReg = {},
            exec, d12, channel, scanN, scanS, i, j;
        for(i in list){
            exec = /([0-9]{12})/.exec(list[i]);
            if(!exec) continue;
            d12 = exec[1];
            channel = false;
            for(j=0; j<dataChannelList.length; j++){
                if(list[i].indexOf(dataChannelList[j]) >= 0){
                    channel = dataChannelList[j];
                    break;
                };
            };
            if(false === channel) continue;

            scanN = true;
            scanS = true;
            if(list[i].indexOf('NORTH') >= 0)
                scanS = false;
            else if(list[i].indexOf('SOUTH') >= 0)
                scanN = false;

            if(!dataFileName[d12]) dataFileName[d12] = {};
            dataFileName[d12][channel] = list[i];

            if(!regionReg[d12]) regionReg[d12] = {north: scanN, south: scanS};
        };

        for(var i in dataFileName) dateStrList.push(i);
        dateStrList.sort();

        var d12;
        for(var i=0; i<dateStrList.length; i++){
            d12 = dateStrList[i];
            menuDiv.append($('<div>')
                .append(
                    $('<input>', {
                        'type': 'checkbox',
                        'id': 'menu-' + dateStrList[i],
                        'value': dateStrList[i],
                    })
                    .data('haveN', regionReg[d12].north)
                    .data('haveS', regionReg[d12].south)
                )
                .append(
                    $('<label>', {'for': 'menu-' + d12})
                        .text(date12ToStr(d12))
                )
                .addClass('map-menu-item')
                .on('click', function(){
                    var checked = (
                        ($(this).find('input:checked').length > 0) &&
                        (!$(this).find('input').attr('disabled'))
                    );
                    if(checked){
                        $(this).addClass('map-menu-item-selected');
                    } else {
                        $(this).removeClass('map-menu-item-selected');
                    }
                })
            );
        };
        menuListFilter();
    };

    function menuListFilter(){
        var menuDiv = $('#' + divID + '-menu');

        var wantN = (0 == dataRegion || 1 == dataRegion),
            wantS = (0 == dataRegion || 2 == dataRegion);

        menuDiv.find('input').each(function(){
            var disable = (
                (wantN && !$(this).data('haveN')) ||
                (wantS && !$(this).data('haveS'))
            );
            $(this).attr('disabled', disable);
        });
        menuListChanged();
    };

    function menuListChanged(){
        var newList = [];
        $('#' + divID + '-menu input:checked').each(function(){
            if($(this).attr('disabled')) return;
            newList.push($(this).val());
        });
        newList.sort();

        var changed = false;
        if(dataDateList.length != newList.length)
            changed = true;
        else {
            for(var i=0; i<newList.length; i++)
                if(newList[i] != dataDateList[i]){
                    changed = true;
                    break;
                };
        };
        if(!changed) return;
        dataDateList = newList;
        dataDate = 0;
        self.toggleCloudAtlas(false);
        updateCloudAtlas();
    };

    $('body').click(function(){
        if(menuStatus){
            self.toggleMenu(false);
            menuListChanged();
        };
    });

    updateCloudAtlas();



    return this;
};


//////////////////////////////////////////////////////////////////////////////
return mapView;
});

