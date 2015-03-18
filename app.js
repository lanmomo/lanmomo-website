var mongoose = require('mongoose');
var express = require('express');
var bodyParser = require('body-parser');
var winston = require('winston');
var morgan = require('morgan');
var app = express();

var config = require('./backend/config/config');

var wrappedMorgan = morgan(
  'dev', {
    stream: {
      write: function(str) {
        winston.info(str.slice(0, - 1));
      }
    }
  }
);

//Database
mongoose.connect(config.db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.use(wrappedMorgan);

//Routing
require('./backend/routes/routes')(app);

app.listen(config.server.port, function() {
  winston.info('Server listening on port %s', config.server.port);
});
