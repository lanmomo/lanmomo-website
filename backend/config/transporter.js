var nodemailer = require('nodemailer');
var credentials = require('./credentials');

var transporter = nodemailer.createTransport({
  //Create a credentials file with skel, update README for instructions
  service: 'Gmail',
  auth: {
    user: credentials.mail.username,
    pass: credentials.mail.password
  }
});

module.exports = transporter;
