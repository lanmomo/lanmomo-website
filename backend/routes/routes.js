var config = require('../config/config');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');
var crypto = require('crypto');

//TODO controllers

module.exports = function(app){
  app.get('/', function(req, res) {
    res.send('public/index.html');
  });

  app.get('/api/users', function(req, res) {
    //TODO Send only specific fields
    User.find({active:true}, function(err, users) {
      //TODO Return 500 if err exists
      res.json(users);
    });
  });

  app.post('/api/subscribe', function(req) {
    req.body.active = false;
    var random = Math.random().toString();
    var hash = crypto.createHash('sha1').update(random).digest('hex');
    User.create(req.body, function(err, user) {
      //TODO Verify err and return 500 if it exists
      var data = {
        userId: user._id,
        emailId: hash
      };
      EmailVerification.create(data, function(err, emailVerification) {
        //TODO Return 500 internal error with err as response
        if(err) console.log(err);
        config.mail.to = req.body.email;
        var hostname = config.server.hostname + config.server.port;
        var url = hostname + "/api/verify/" + emailVerification.emailId;
        config.mail.subject = 'Vérification de courriel';
        config.mail.html = 'Veuillez confirmer votre courriel en cliquant <a href=\"' + url + '\">ici</a>';
        config.transporter.sendMail(config.mail, function(err, info) {
          //TODO Return 500 internal with err as response
          if(err) console.log(err);
          console.log(info.response);
        });
      });
    });
  });

  app.get('/api/verify/:emailId', function(req, res) {
    EmailVerification.findOne({emailId: req.param('emailId')}, function(err, emailVerification) {
      //TODO Return 500 if err
      if(err) console.log(err);
      //TODO Do not continue if err
      User.update({_id: emailVerification.userId}, {active: true}, function(err, numAffected) {
        //TODO Create an error page instead of congratulations
        if(err) console.log(err);
        console.log(numAffected);
        var url = config.server.hostname + config.server.port + '/#/congratulations';
        res.redirect(url);
      });
    });
  });
};
