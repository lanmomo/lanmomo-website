var nodemailer = require('nodemailer');
var smtpTransport = require('nodemailer-smtp-transport');
var extend = require('extend');
var P = require('bluebird');

var config = require('./config.default.js');
var envConfig = require('./config.' + process.env.NODE_ENV + '.js') || {};

extend(true, config, envConfig); // Merge envConfig into default config

var transporter = nodemailer.createTransport(smtpTransport(config.mailer.transportOptions));
config.transporter = P.promisifyAll(transporter);

module.exports = config;
