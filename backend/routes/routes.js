var config = require('../config/config');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');
var crypto = require('crypto');

module.exports = function(app){
  app.get('/', function(req, res) {
    res.send('public/index.html');
  });

  app.get('/api/users', function(req, res) {
    User.find({active:true},'username firstname lastname', function(err, users) {
      res.json(users);
    });
  });

  app.post('/api/subscribe', function(req) {
    req.body.active = false;
    //TODO make this more robuste
    var random = Math.random().toString();
    var hash = crypto.createHash('sha1').update(random).digest('hex');
    User.create(req.body, function(err, user) {
      var data = {
        userId: user._id,
        emailId: hash
      };
      EmailVerification.create(data, function(err, emailVerification) {
        if(err) console.log(err);
        config.mail.to = req.body.email;
        //TODO change to the dns
        //TODO hostname from config?
        //TODO hostname + port
        var hostname = "http://localhost:3000";
        var url = hostname + "/api/verify/" + emailVerification.emailId;
        config.mail.html = 'Veuillez confirmer votre courriel en cliquant <a href=\"' + url + '\">ici</a>';
        config.transporter.sendMail(config.mail, function(err, info) {
          if(err) console.log(err);
          console.log(info.response);
        });
      });
    });
  });

  app.get('/api/verify/:emailId', function(req, res) {
    EmailVerification.findOne({emailId: req.param('emailId')}, function(err, emailVerification) {
      if(err) console.log(err);
      User.update({_id: emailVerification.userId}, {active: true}, function(err, numAffected) {
        if(err) console.log(err);
        console.log(numAffected);
        //TODO change to the dns in production
        res.redirect('http://localhost:3000/#/congratulations');
      });
    });
  });
};
