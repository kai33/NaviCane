var socket = io.connect('http://localhost');
var paper;
var personObjs = {};
var persons = {};
var personNames = {};
var WIDTH = 1228;
var HEIGHT = 335;
var SIDE_LIMIT = 64;
var HALF_SIDE_LIMIT = SIDE_LIMIT / 2;
var RADIUS = 5;
var TEXT_OFF_BY = 8;
var SCALE_FACTOR = 0.1;
var indicatorPath = 'M21.871,9.814 15.684,16.001 21.871,22.188 18.335,25.725 8.612,16.001 18.335,6.276z';
socket.on('greeting', function (data) {
    socket.emit('ready', { status: 'ready' });
});
socket.on('mapInfo', function (data) {
    var arrowPath = 'M15.834,29.084 15.834,16.166 2.917,16.166 29.083,2.917z';
    paper = Raphael(50, 50, WIDTH + SIDE_LIMIT, HEIGHT + SIDE_LIMIT);
    var northAt = parseInt(data.info.northAt) - 45;
    var arrow = paper.path(arrowPath).attr('fill', '#000').transform('r' + northAt);
    console.log(data);
    for (var i = 0; i < data.map.length; i++) {
        var objX = mapAcutalValueToMap(parseInt(data.map[i]['x']), false);
        var objY = mapAcutalValueToMap(parseInt(data.map[i]['y']), true);
        var neighbors = data.map[i]['linkTo'].split(',');
        for (var j = 0; j < neighbors.length; j++) {
            var idx = parseInt(neighbors[j].trim()) - 1;
            var neighbor = data.map[idx];
            var neighborX = mapAcutalValueToMap(parseInt(neighbor['x']), false);
            var neighborY = mapAcutalValueToMap(parseInt(neighbor['y']), true);
            var path = paper.path('M' + objX + ',' + objY + 'L' + neighborX + ',' + neighborY);
        }
    }
    for (var i = 0; i < data.map.length; i++) {
        var objX = mapAcutalValueToMap(parseInt(data.map[i]['x']), false);
        var objY = mapAcutalValueToMap(parseInt(data.map[i]['y']), true);
        var nodeName = data.map[i]['nodeName'];
        var circle = paper.circle(objX, objY, RADIUS).attr("fill", "#f00");
        var text = paper.text(objX, objY - TEXT_OFF_BY, nodeName);
    }
});
socket.on('usersInfo', function (data) {
    var url = window.location.href;
    var splitedUrl = url.split('/');
    var building = splitedUrl[splitedUrl.length - 2];
    var level = splitedUrl[splitedUrl.length - 1];
    for (var prop in data) {
        if (data.hasOwnProperty(prop)) {
            var obj = data[prop];
            if (obj.building === building && obj.level === level) {
                if (!persons[prop]) {
                    persons[prop] = paper.path(indicatorPath).attr('fill', '#0ff').transform('r45');
                    personNames[prop] = paper.text(10, 5, prop.toString()).attr('fill', '#f0f');
                }
                var person = persons[prop];
                var personName = personNames[prop];
                var transformX = mapAcutalValueToMap(obj.x, false);
                var transformY = mapAcutalValueToMap(obj.y, true);
                var transformRotation = obj.direction;
                person.transform('t' + transformX + ',' + transformY + 'r' + transformRotation);
                personName.transform('t' + transformX + ',' + transformY);
                if (personObjs[prop]) {
                    var prevX = mapAcutalValueToMap(personObjs[prop].x, false);
                    var prevY = mapAcutalValueToMap(personObjs[prop].y, true);
                    var currX = mapAcutalValueToMap(obj.x, false);
                    var currY = mapAcutalValueToMap(obj.y, true);
                    paper.path('M' + prevX + ',' + prevY + 'L' + currX + ',' + currY).attr('fill', '#a0a');
                }
                personObjs[prop] = obj;
                console.log('updating');
            }
        }
    }
});

function mapAcutalValueToMap (value, isY) {
    if (isY) {
        return HEIGHT - value * SCALE_FACTOR + HALF_SIDE_LIMIT;
    } else {
        return value * SCALE_FACTOR + HALF_SIDE_LIMIT;
    }
}
