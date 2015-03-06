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
    //TODO Return 500 if err exists
    User.find({active:true},'username firstname lastname', function(err, users) {
      res.json(users);
    });
  });

  app.post('/api/subscribe', function(req, res) {
    if(validateBody(req.body)) {
      req.body.active = false;
      //TODO make this more robuste
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
          var url = config.server.hostname + "/api/verify/" + emailVerification.emailId;
          config.mail.subject = 'Vérification de courriel';
          config.mail.html = 'Veuillez confirmer votre courriel en cliquant <a href=\"' + url + '\">ici</a>';
          config.transporter.sendMail(config.mail, function(err, info) {
            //TODO Return 500 internal with err as response
            if(err) console.log(err);
            //TODO Send feedback to user
            console.log(info.response);
          });
        });
      });
    } else {
      return res.status(400).json({message:'Les informations données sont invalides ou incomplètes'});
    }
  });

  app.get('/api/verify/:emailId', function(req, res) {
    if(req.param('emailId')){
      EmailVerification.findOne({emailId: req.param('emailId')}, function(err, emailVerification) {
        if(err || emailVerification === null) {
            res.status(400).send('Mauvaise url');
        } else {
          User.update({_id: emailVerification.userId}, {active: true}, function(err) {
            if (err) {
              res.status(500).json({message:'Erreur lors de la modification de l\'utilisateur'});
            } else {
              var url = 'http://' + config.server.hostname + '/#/congratulations';
              res.redirect(url);
            }
          });
        }
      });
    } else {
      res.status(400).send('Mauvais paramètre');
    }
  });
};

var validateBody = function(body){
  return body.username && body.email && body.firstname && body.lastname;
};
