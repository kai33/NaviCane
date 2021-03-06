var express = require('express');
var app = express();
var request = require("request");
var serveStatic = require('serve-static');
var bodyParser = require('body-parser');
var path = require('path');
var server = app.listen(3000, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('app listening at http://%s:%s', host, port);
});
var io = require('socket.io')(server);
var mapInfo;
var users = {T10: {building: '1', level: '2', x: 32, y: 40, direction: 270}};

app.use(bodyParser.urlencoded({
  extended: true
}));
app.use(bodyParser.json());
app.use('/static', serveStatic(path.join(__dirname, 'public')));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');

app.get('/monitor/:building/:level', function (req, res) {
    var building = req.params.building;
    var level = req.params.level;
    var requestUrl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=' + building + '&Level=' + level;
    request({
        url: requestUrl,
        json: true
    }, function (error, response, body) {
        if (!error && response.statusCode === 200) {
            mapInfo = body;
        }
    });
    res.render('monitor.ejs', {building: building, level: level});
});

app.post('/users/', function (req, res) {
    var user = req.body;
    users[user['user_id']] = user;
    io.sockets.emit('usersInfo', users);
    res.sendStatus(200);
});

io.on('connection', function (socket) {
    socket.emit('greeting', { hello: 'ready' });
    socket.on('ready', function (data) {
        if (mapInfo) {
            socket.emit('mapInfo', mapInfo);
        }
    });
});
