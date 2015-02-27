var nodemailer = require('nodemailer');

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    user: 'lanmomo.noreply@gmail.com',
    pass: 'lanmomo2015'
  }
});

module.exports = transporter;
