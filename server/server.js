var app = require('http').createServer(handler)
var io = require('socket.io')(app);
var fs = require('fs');

app.listen(10086);

function handler(req, res){
    res.writeHead(200);
    res.end('SocketIO server for map tiles running.');
}

io.on('connection', function (socket){
    socket.emit('connected');
    socket.on('tile', serveTile);
    socket.on('list', serveList);
    socket.on('geoJSON', serveGeoJSON);
});



/* serve tiles */

function serveTile(req){
    
};

/* serve geoJSON */

function serveGeoJSON(req){
};

/* serve a list of files */

function serveList(){
};
