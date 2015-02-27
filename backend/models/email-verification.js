var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var emailVerificationSchema = new Schema({
  userId: {type: Schema.Types.ObjectId, ref: 'User'},
  emailId: String
});

module.exports = mongoose.model('EmailVerification', emailVerificationSchema);
