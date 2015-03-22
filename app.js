var mongoose = require('mongoose');
var express = require('express');
var bodyParser = require('body-parser');
var app = express();

var config = require('./backend/config/config');
var logger = require('./backend/lib/logger');

//Database
mongoose.connect(config.db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

//DEV only
if (process.env.NODE_ENV == 'dev') {
  var morgan = require('./backend/lib/morgan');
  app.use(morgan);
}

//Routing
require('./backend/routes/routes')(app);

app.listen(config.server.port, function() {
  logger.info('Server listening on port %s', config.server.port);
});
