var config = require('../config/config');
var logger = require('../lib/logger');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');
var crypto = require('crypto');
var util = require('util');
var P = require('bluebird');
var template = require('../templates/mail');

var validateBody = function(body) {
  var emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  var phoneRegex = /^([+]?1[. -]?)?[(]?[0-9]{3}[)]?[. -]?[0-9]{3}[. -]?[0-9]{4}$/i;

  return emailRegex.test(body.email) && phoneRegex.test(body.phone) && body.username && body.firstname && body.lastname && config.types.indexOf(body.type) >= 0;
};

var verifyUniqueEmail = function(req, res) {
  User.count().or([{username:req.body.username}, {email:req.body.email}]).exec()
  .then(function(count) {
    if (count > 0) {
      res.status(402).json({message:"Votre courriel ou votre nom d'utilisateur sont déjà utilisés."});
    } else {
      verifyMaximum(req, res);
    }
  })
  .reject(function(err) {
    logger.error('Error occured while finding users matching username or email: %s', err, req.body);
    res.status(500).json({message: "Une erreur interne est survenue lors de la recherche du courriel et du nom d'utilisateur"});
  });
};

var verifyMaximum = function(req, res) {
  var type = req.body.type;
  User.where({active:true}, {"type":type}).count().exec()
  .then(function(count) {
    if (count >= config.maximum[type]) {
      res.status(402).json({message:"Le nombre maximum de participants sur " + type + " a été atteint."});
    } else {
      createUser(req, res);
    }
  })
  .reject(function(err) {
    logger.error('Error occured while finding active users matching type: %s', err, req.body);
    res.status(500).json({message: "Une erreur est survenue lors de la recherche des participants"});
  });
};

var createUser = function(req, res) {
  req.body.active = false;
  User.create(req.body)
  .then(function(user) {
    createEmailVerification(req, res, user);
  })
  .reject(function(err) {
    logger.error('Error occured while creating user: %s', err, req.body);
    res.status(500).json({message:"Une erreur est survenue lors de la création d'un participant"});
  });
};

var createEmailVerification = function(req, res, user) {
  var confirmId = crypto.randomBytes(42).toString('hex');
  var data = {
    userId: user._id,
    emailId: confirmId
  };
  EmailVerification.create(data)
  .then(function(emailVerification) {
    sendMail(req, res, emailVerification, user);
  })
  .reject(function(err) {
    logger.error('Error occured while creating mail: %s', err, data);
    res.status(500).json({message: "Une erreur interne est survenue de la création du courriel de validation"});
  });
};

var sendMail = function(req, res, emailVerification, user) {
  var url = config.url.root + '/api/verify/' + emailVerification.emailId;
  createEmail(url, emailVerification, user)
  .then(function(html) {
    var mail = {
      from: config.mailer.from,
      to: req.body.email,
      subject: 'Vérification de courriel',
      html: html
    };
    config.transporter.sendMailAsync(mail)
    .then(function(info) {
      logger.debug(info);
      res.status(200).json({message:"Veuillez confirmer votre inscription en allant dans votre boîte de réception."});
    })
    .catch(function(err) {
      logger.error('Error occured while sending mail: %s', err, mail);
      res.status(500).json({message: "Une erreur interne est survenue lors de l'envoi du courriel de validation"});
    });
  })
  .catch(function(err) {
    logger.error('Error occured while creating email html template : %s', err);
    res.status(500).json({message: "Une erreur interne est survenue lors de l'envoi du courriel de validation"});
  });
};

var createEmail = function(url, emailVerification, user) {
  return new P(function(resolve) {
    logger.debug('Sending email to %s', user);
    var html = util.format(template, user.firstname, url, url);
    resolve(html);
  });
};

var updateUser = function(req, res, emailVerification) {
  logger.debug(emailVerification);
  User.update({_id: emailVerification.userId}, {active: true}).exec()
  .then(function() {
    var url = config.url.root + '/congratulations';
    logger.debug(url);
    res.redirect(url);
  })
  .reject(function(err) {
    logger.error('Error occured while activation user: %s', err, emailVerification);
    res.status(500).json({message:"Erreur lors de la modification de l'utilisateur"});
  });
};

exports.index = function(req, res) {
  res.sendFile('index.html', {root: __dirname + '/../../public/'});
};

exports.getAll = function(req, res) {
  User.find({active:true}).select('username firstname lastname type').exec()
  .then(function(users) {
    res.json(users);
  })
  .reject(function(err) {
    logger.error('Error occured while finding users: %s', err);
    res.status(500).json({message:"Une erreur interne est survenue lors de la recherche des participants"});
  });
};

exports.getMax = function(req, res) {
  var type = req.params.type;
  res.json({maxUsers:config.maximum[type]});
};

exports.subscribe = function(req, res) {
  if (validateBody(req.body)) {
    verifyUniqueEmail(req, res);
  } else {
    return res.status(400).json({message:'Les informations données sont invalides ou incomplètes'});
  }
};

exports.verify = function(req, res) {
  if (req.params.emailId) {
    EmailVerification.findOne({emailId: req.params.emailId}).exec()
    .then(function(emailVerification) {
      updateUser(req, res, emailVerification);
    })
    .reject(function(err) {
      logger.warn('Error occured while finding emailVerification `%s`: %s', req.params.emailId, err);
      res.status(400).send('Mauvaise url');
    });
  } else {
    res.status(400).send('Mauvais paramètre');
  }
};
