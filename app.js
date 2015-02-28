var mongoose = require('mongoose');
var express = require('express');
var crypto = require('crypto');
var bodyParser = require('body-parser');
var app = express();
var db = require('./backend/config/db');

//Database
mongoose.connect(db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));

//Routing
require('./backend/routes/routes')(app);

//TODO Using configuration for port
app.listen(3000);
console.log("Listening on port 3000");
