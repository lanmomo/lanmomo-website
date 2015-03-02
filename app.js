var mongoose = require('mongoose');
var express = require('express');
var crypto = require('crypto');
var bodyParser = require('body-parser');
var app = express();
var db = require('./backend/config/db');
var server = require('./backend/config/server');

//Database
mongoose.connect(db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));

//Routing
require('./backend/routes/routes')(app);

app.listen(server.port, function() {
  console.log('Server listening on port ' + server.port);
});
