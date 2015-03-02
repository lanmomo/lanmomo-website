var nodemailer = require('nodemailer');
var credentials = require('./credentials');

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: credentials.mail.username,
    pass: credentials.mail.password
  }
});

module.exports = transporter;
