var nodemailer = require('nodemailer');
var credentials = require('./credentials');

var config = require('./config.' + process.env.NODE_ENV + '.js');

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: credentials.mail.username,
    pass: credentials.mail.password
  }
});

var mail = {
  from: 'Lan Montmorency'
};

config.transporter = transporter;
config.mail = mail;

module.exports = config;
