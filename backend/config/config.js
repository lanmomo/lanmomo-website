var nodemailer = require('nodemailer');

var config = require('./config.' + process.env.NODE_ENV + '.js');

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: config.mail.username,
    pass: config.mail.password
  }
});

config.mail.from = 'Lan Montmorency';

config.transporter = transporter;

module.exports = config;
