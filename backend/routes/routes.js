var tranporter = require('../config/transporter');
var mailOptions = require('../config/mail-options');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');

module.exports = function(app){
  app.get('/', function(req, res) {
    res.send('public/index.html');
  });

  app.get('/api/users', function(req, res) {
    User.find({}, function(err, users) {
      res.json(users);
    });
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
}
