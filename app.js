var mongoose = require('mongoose');
var express = require('express');
var crypto = require('crypto');
var bodyParser = require('body-parser');
var app = express();
var db = require('./backend/config/db');
var tranporter = require('./backend/config/transporter');
var mailOptions = require('./backend/config/mail-options');
var User = require('./backend/models/user');
var EmailVerification = require('./backend/models/email-verification');

//Database
mongoose.connect(db.url);

//Middleware
app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended:true}));

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

app.post('/api/subscribe', function(req, res) {
  req.body.active = false;
  var random = Math.random().toString();
  var hash = crypto.createHash('sha1').update(random).digest('hex');
  User.create(req.body, function(err, user) {
    data = {
      userId: user._id,
      emailId: hash
    }
    EmailVerification.create(data, function(err, emailVerification) {
      mailOptions.to = req.body.email;
      //TODO change to the dns
      //TODO hostname from config?
      hostname = "http://localhost:3000";
      url = hostname + "/api/verify/" + hash;
      mailOptions.html = 'Veuillez confirmer votre courriel en cliquant <a href=\"' + url + '\">ici</a>';
      tranporter.sendMail(mailOptions, function(err, info) {
        if(err) console.log(err);
        console.log(info.response);
      });
    });
  });
});

app.get('/api/verify/:emailId', function(req, res) {
  EmailVerification.findOne({emailId: req.param('emailId')}, function(err, emailVerification) {
    if(err) log(err);
      User.update({_id: emailVerification.userId}, {active: true}, function(err, numAffected) {
        if(err) console.log(err);
        console.log(numAffected);
        //TODO change to the dns in production
        res.redirect('http://localhost:3000/#/congratulations');
      });
  });
});

app.listen(3000, function() {
  console.log('Server listening on port 3000');
});
