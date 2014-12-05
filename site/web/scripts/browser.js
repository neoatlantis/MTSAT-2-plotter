require([
    'jquery',
    'socket.io',
    'map',
], function(
    $,
    io,
    map
){
//////////////////////////////////////////////////////////////////////////////
/* necessary configurations */

var webServerHost = 'mtsat-2.neoatlantis.org';
var webServerSocketURL = 'http://mtsat-2.neoatlantis.org:10086';
var webServerSocketTimeout = 5000;

/****************************************************************************/
if(window.location.hostname == 'localhost'){
    // for debug conveniences
    webServerSocketURL = 'http://localhost:10086';
    webServerHost = 'localhost';
    webServerSocketTimeout = 500;
};

$('#start').empty();
function log(s){ $('#start').append($('<div>').text(s)); };

log('Javascript加载完毕。');
log('正在尝试使用WebSocket连接服务器...等待5秒...');

var socketTimedout = false, socketUseable = false;
/*var socket = io(webServerSocketURL);
socket.on('connected', function(){
    if(socketTimedout) return;
    socketUseable = true;
    log('已确认服务器连接。');
    initConnection();
});*/
setTimeout(function(){
    if(socketUseable) return;
    socketTimedout = true;
    log('WebSocket方法无法连接到服务器。');

    if(window.location.hostname != webServerHost){
        log(
            '错误：您当前访问的数据浏览器处于一个镜像服务器上，' +
            '无法通过传统方式（跨域名）访问主服务器上的数据。'
        );
        log('请访问位于' + webServerHost + '的服务器，或更换一个镜像。');
        log('程序停止。');
        return;
    };

    initConnection();
}, webServerSocketTimeout);


var downloadTile = false, downloadGeoJSON = false;
function initConnection(){
    if(socketUseable){
        log('程序设定为使用WebSocket连接获取数据。');
        downloadTile = function(filename, z, x, y, format, callback){
        };
    } else {
        log('程序设定为使用传统方式获取数据。');
    };

    initMap();
};

function initMap(){
    var mapView = new map(
        'map',
        {
            tile: downloadTile,
        }
    );
    
    $('#start').addClass('hidden');
    $('#map').removeClass('hidden');
    
    $.get('/data/index.txt', function(txt){
        var list = txt.split('\n'), l = [];
        for(var i=0; i<list.length; i++){
            list[i] = list[i].trim();
            if('' != list[i] && 'index.txt' != list[i]) l.push(list[i]);
        };
        mapView.assignList(l);
    });
};

//////////////////////////////////////////////////////////////////////////////
});
