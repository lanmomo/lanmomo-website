var nodemailer = require('nodemailer');
var smtpTransport = require('nodemailer-smtp-transport');
var P = require('bluebird');

var config = require('./config.' + process.env.NODE_ENV + '.js');

var transporter = P.promisifyAll(nodemailer.createTransport(smtpTransport(config.mailer.transportOptions)));

config.transporter = transporter;

module.exports = config;
