var nodemailer = require('nodemailer');

var transporter = nodemailer.createTransport({
  //Create a credentials file with skel, update README for instructions
  service: 'Gmail',
  auth: {
    user: 'lanmomo.noreply@gmail.com',
    pass: 'montmorency2015'
  }
});

module.exports = transporter;
