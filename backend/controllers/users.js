var config = require('../config/config');
var logger = require('../lib/logger');
var User = require('../models/user');
var EmailVerification = require('../models/email-verification');
var crypto = require('crypto');
var util = require('util');
var P = require('bluebird');
var template = require('../templates/mail');

function validateBody(body) {
  var emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  var phoneRegex = /^([+]?1[. -]?)?[(]?[0-9]{3}[)]?[. -]?[0-9]{3}[. -]?[0-9]{4}$/i;

  return emailRegex.test(body.email) && phoneRegex.test(body.phone) && body.username && body.firstname && body.lastname && config.types.indexOf(body.type) >= 0;
};

function verifyUniqueEmail(req, res) {
  var email = req.body.email;
  User.findOneByEmail(email)
  .then(function(user) {
    if(user) {
      res.status(402).json({message:"Votre courriel est déjà utilisé."});
    } else {
      verifyUniqueUsername(req, res);
    }
  })
  .reject(function(err) {
    logger.error('Error occured while finding users matching username or email: %s', err, req.body);
    res.status(500).json({message: "Une erreur interne est survenue lors de la recherche du courriel et du nom d'utilisateur"});
  });
}

function verifyUniqueUsername(req, res) {
  var username = req.body.username;
  User.findOneByUsername(username)
  .then(function(user) {
    if(user) {
      res.status(402).json({message:"Votre nom d'utilisateur est déjà utilisé."});
    } else {
      verifyMaximum(req, res);
    }
  })
  .reject(function(err) {
    logger.error('Error occured while finding users matching username or email: %s', err, req.body);
    res.status(500).json({message: "Une erreur interne est survenue lors de la recherche du courriel et du nom d'utilisateur"});
  });
}

function verifyMaximum(req, res) {
  var type = req.body.type;
  User.count().and([{active:true}, {"type":type}]).exec()
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

function createUser(req, res) {
  req.body.active = false;
  req.body.phone = req.body.phone.replace(/\D+/g, ''); // Remove all none-digit characters
  if (validateUser(req.body)) {
    User.create(req.body)
    .then(function(user) {
      createEmailVerification(req, res, user);
    })
    .reject(function(err) {
      logger.error('Error occured while creating user: %s', err, req.body);
      res.status(500).json({message:"Une erreur est survenue lors de la création d'un participant"});
    });
  } else {
    res.status(400).json({message:"La requête contient des données non conformes."});
  }
};

function validateUser(user) {
  return validateLength(user.username, 4, 32) && validateLength(user.firstname, 2, 32) && validateLength(user.lastname, 2, 32);
};

function validateLength(field, min, max) {
  return field.length <= max && field.length >= min;
};

function createEmailVerification(req, res, user) {
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

function sendMail(req, res, emailVerification, user) {
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

function createEmail(url, emailVerification, user) {
  return new P(function(resolve) {
    logger.debug('Sending email to %s', user);
    var html = util.format(template, user.firstname, url, url);
    resolve(html);
  });
};

function updateUser(req, res, emailVerification) {
  logger.debug(emailVerification);
  User.update({_id: emailVerification.userId}, {active: true}).exec()
  .then(function() {
    redirect(res, 'congratulations');
  })
  .reject(function(err) {
    logger.error('Error occured while activation user: %s', err, emailVerification);
    res.status(500).json({message:"Erreur lors de la modification de l'utilisateur"});
  });
};

function redirect(res, partial) {
  var url = config.url.root + '/' + partial;
  logger.debug(url);
  res.redirect(url);
}

exports.index = function index(req, res) {
  res.sendFile('index.html', {root: __dirname + '/../../public/'});
};

exports.getAll = function getAll(req, res) {
  User.find({active:true}).select('username firstname lastname type').exec()
  .then(function(users) {
    res.json(users);
  })
  .reject(function(err) {
    logger.error('Error occured while finding users: %s', err);
    res.status(500).json({message:"Une erreur interne est survenue lors de la recherche des participants"});
  });
};

exports.getMax = function getMax(req, res) {
  var type = req.params.type;
  res.json({maxUsers:config.maximum[type]});
};

exports.isMax = function isMax(req, res) {
  var max = {
    pc: false,
    console: false,
    both: false
  };
  User.where({active:true}).and({type:'pc'}).count().exec()
    .then(function(count) {
      max.pc = (count >= config.maximum.pc);
      User.where({active:true}).and({type:'console'}).count().exec()
        .then(function(count) {
          max.console = (count >= config.maximum.console);
          max.both = (max.pc && max.console);
          res.json({max:max});
        })
        .reject(function(err) {
          logger.error('Error occured while finding active users matching type: %s', err);
          res.status(500).json({message: "Une erreur est survenue lors de la recherche des participants"});
        });
    })
    .reject(function(err) {
      logger.error('Error occured while finding active users matching type: %s', err);
      res.status(500).json({message: "Une erreur est survenue lors de la recherche des participants"});
    });
};

exports.hasUsername = function hasUsername(req, res) {
  User.where({username:req.body.username}).count().exec()
    .then(function(count) {
      if (count > 0) {
        res.status(200).json({exists: true});
      } else {
        res.status(200).json({exists: false});
      }
    })
    .reject(function(err) {
      logger.error('Error occured while finding users matching username: %s', err, req.body);
      res.status(500).send('Une erreur interne est survenue');
    });
};

exports.hasEmail = function hasEmail(req, res) {
  User.where({email:req.body.email}).count().exec()
    .then(function(count) {
      if (count > 0) {
        res.status(200).json({exists: true});
      } else {
        res.status(200).json({exists: false});
      }
    })
    .reject(function(err) {
      logger.error('Error occured while finding users matching email: %s', err, req.body);
      res.status(500).send('Une erreur interne est survenue');
    });
};

exports.subscribe = function subscribe(req, res) {
  if (validateBody(req.body)) {
    verifyUniqueEmail(req, res);
  } else {
    return res.status(400).json({message:'Les informations données sont invalides ou incomplètes'});
  }
};

exports.verify = function verify(req, res) {
  if (req.params.emailId) {
    EmailVerification.findOne({emailId: req.params.emailId}).exec()
    .then(function(emailVerification) {
      if (emailVerification.confirmed) {
        redirect(res, 'confirmed');
      } else {
        updateEmailVerification(req, res, emailVerification);
      }
    })
    .reject(function(err) {
      logger.warn('Error occured while finding emailVerification `%s`: %s', req.params.emailId, err);
      res.status(400).send('Mauvaise url');
    });
  } else {
    res.status(400).send('Mauvais paramètre');
  }
};

function updateEmailVerification(req, res, emailVerification) {
  emailVerification.confirmed = true;
  emailVerification.save(function(err) {
    updateUser(req, res, emailVerification);
  });
}
