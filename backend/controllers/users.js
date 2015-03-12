var config = require('../config/config');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');
var crypto = require('crypto');

var validateBody = function (body) {
  return body.username && body.email && body.firstname && body.lastname;
};

exports.index = function (req, res) {
  res.send('public/index.html');
};

exports.getAll = function (req, res) {
  User.find({active:true}).select('username firstname lastname').exec()
  .then(function (users) {
    res.json(users);
  })
  .reject(function (err) {
    console.log(err);
    res.status(500).json({message:"Une erreur interne est survenue lors de la recherche des participants"});
  });
};

exports.subscribe = function (req, res) {
  if (validateBody(req.body)) {
    req.body.active = false;
    var confirmId = crypto.randomBytes(42).toString('hex');
    User.create(req.body)
    .then(function (user) {
      var data = {
        userId: user._id,
        emailId: confirmId
      };
      EmailVerification.create(data)
      .then(function (emailVerification) {
        config.mail.to = req.body.email;
        var url = config.server.hostname + "/api/verify/" + emailVerification.emailId;
        config.mail.subject = 'Vérification de courriel';
        config.mail.html = 'Veuillez confirmer votre courriel en cliquant <a href=\"' + url + '\">ici</a>';
        config.transporter.sendMail(config.mail)
        .then(function (info) {
          //TODO Send feedback to user
          console.log(info);
        })
        .catch(function (err) {
          console.log(err);
          res.status(500).json({message: "Une erreur interne est survenue lors de l'envoi du courriel de validation"});
        });
      })
      .reject(function (err) {
        console.log(err);
        res.status(500).json({message: "Une erreur interne est survenue de la création du courriel de validation"});
      });
    })
    .reject(function (err) {
      console.log(err);
      res.status(500).json({message:"Une erreur est survenue lors de la création d'un participant"});
    });
  } else {
    return res.status(400).json({message:'Les informations données sont invalides ou incomplètes'});
  }
};

exports.verify = function (req, res) {
  if (req.param('emailId')) {
    EmailVerification.findOne({emailId: req.param('emailId')}).exec()
    .then(function (emailVerification) {
      console.log(emailVerification);
      User.update({_id: emailVerification.userId}, {active: true}).exec()
      .then(function () {
        var url = 'http://' + config.server.hostname + '/#/congratulations';
        console.log(url);
        res.redirect(url);
      })
      .reject(function (err) {
        console.log(err);
        res.status(500).json({message:'Erreur lors de la modification de l\'utilisateur'});
      });
    })
    .reject(function (err) {
      console.log(err);
      res.status(400).send('Mauvaise url');
    });
  } else {
    res.status(400).send('Mauvais paramètre');
  }
};
