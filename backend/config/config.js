var nodemailer = require('nodemailer');
var credentials = require('./credentials');
var config = {};

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

//TODO config = require('./config.' + process.env.NODE_ENV + '.js')

switch(process.env.NODE_ENV) {
  case 'dev':
    config = {server:{port:3000}, db:{url:'mongodb://localhost/dev'}};
    break;
  case 'prod':
    //TODO Credentials for production database
    config = {server:{port:80}, db:{url:'mongodb://localhost/lanmomo'}};
    break;
}

config.transporter = transporter;
config.mail = mail;

module.exports = config;
