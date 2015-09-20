var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var emailVerificationSchema = new Schema({
  userId: {type: Schema.Types.ObjectId, ref: 'User'},
  emailId: {type: String, trim: true},
  confirmed: Boolean
});

module.exports = mongoose.model('EmailVerification', emailVerificationSchema);
