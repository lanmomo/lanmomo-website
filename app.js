var mongoose = require('mongoose');
var express = require('express');
var app = express();
var db = require('./backend/config/db');
var User = require('./backend/models/user');

//Database
mongoose.connect(db.url);

//Middleware
app.use(express.static(__dirname + '/public'));

//Routing
//TODO Should be in backend/routes/routes
app.get('/', function(req, res) {
  res.send('public/index.html');
});

app.get('/api/users', function(req, res) {
  User.find({}, function(err, users) {
    res.json(users);
  })
});

app.listen(3000);
console.log("Listening on port 3000");
