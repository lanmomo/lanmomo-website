var mongoose = require('mongoose');
var express = require('express');
var bodyParser = require('body-parser');
var morgan = require('morgan');
var app = express();

var config = require('./backend/config/config');

//Database
mongoose.connect(config.db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.use(morgan('dev'));

//Routing
require('./backend/routes/routes')(app);

app.listen(config.server.port, function() {
  console.log('Server listening on port ' + config.server.port);
});
