var nodemailer = require('nodemailer');
var P = require('bluebird');

var config = require('./config.' + process.env.NODE_ENV + '.js');

var options = {
  service: 'Gmail',
  auth: {
    user: config.mail.username,
    pass: config.mail.password
  }
};
var transporter = P.promisifyAll(nodemailer.createTransport(options));

config.mail.from = 'Lan Montmorency';

config.transporter = transporter;

module.exports = config;
