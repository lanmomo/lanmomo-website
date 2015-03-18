var mongoose = require('mongoose');
var express = require('express');
var bodyParser = require('body-parser');
var app = express();

var config = require('./backend/config/config');
var logger = require('./backend/lib/logger');
var morgan = require('./backend/lib/morgan');

//Database
mongoose.connect(config.db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.use(morgan);

//Routing
require('./backend/routes/routes')(app);

app.listen(config.server.port, function() {
  logger.info('Server listening on port %s', config.server.port);
});
