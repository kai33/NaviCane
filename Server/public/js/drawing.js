var socket = io.connect('http://localhost');
var person;
socket.on('greeting', function (data) {
    socket.emit('ready', { status: 'ready' });
});
socket.on('mapInfo', function (data) {
    var SIDE_LIMIT = 64;
    var HALF_SIDE_LIMIT = SIDE_LIMIT / 2;
    var RADIUS = 5;
    var TEXT_OFF_BY = 8;
    var SCALE_FACTOR = 0.1;
    var arrowPath = 'M15.834,29.084 15.834,16.166 2.917,16.166 29.083,2.917z';
    var paper = Raphael(50, 50, 1228 + SIDE_LIMIT, 335 + SIDE_LIMIT);
    var northAt = parseInt(data.info.northAt) - 45;
    var arrow = paper.path(arrowPath).attr('fill', '#000').transform('r' + northAt);
    var indicatorPath = 'M21.871,9.814 15.684,16.001 21.871,22.188 18.335,25.725 8.612,16.001 18.335,6.276z';
    person = paper.path(indicatorPath).attr('fill', '#aaa').transform('r90');
    console.log(data);
    for (var i = 0; i < data.map.length; i++) {
        var objX = parseInt(data.map[i]['x']) * SCALE_FACTOR + HALF_SIDE_LIMIT;
        var objY = parseInt(data.map[i]['y']) * SCALE_FACTOR + HALF_SIDE_LIMIT;
        var neighbors = data.map[i]['linkTo'].split(',');
        for (var j = 0; j < neighbors.length; j++) {
            var idx = parseInt(neighbors[j].trim()) - 1;
            var neighbor = data.map[idx];
            var neighborX = parseInt(neighbor['x']) * SCALE_FACTOR + HALF_SIDE_LIMIT;
            var neighborY = parseInt(neighbor['y']) * SCALE_FACTOR + HALF_SIDE_LIMIT;
            var path = paper.path('M' + objX + ',' + objY + 'L' + neighborX + ',' + neighborY);
        }
    }
    for (var i = 0; i < data.map.length; i++) {
        var objX = parseInt(data.map[i]['x']) * SCALE_FACTOR;
        var objY = parseInt(data.map[i]['y']) * SCALE_FACTOR;
        var nodeName = data.map[i]['nodeName'];
        var circle = paper.circle(objX + HALF_SIDE_LIMIT, objY + HALF_SIDE_LIMIT, RADIUS).attr("fill", "#f00");
        var text = paper.text(objX + HALF_SIDE_LIMIT, objY + HALF_SIDE_LIMIT - TEXT_OFF_BY, nodeName);
    }
    socket.emit('request', { status: 'requestUserData'});
});
socket.on('userInfo', function (data) {
    var url = window.location.href;
    var splitedUrl = url.split('/');
    var building = splitedUrl[splitedUrl.length - 2];
    var level = splitedUrl[splitedUrl.length - 1];
    if (building === data.building && level === data.level) {
        console.log(data.x);
        console.log(data.y);
        console.log(data.direction);
    }
});
