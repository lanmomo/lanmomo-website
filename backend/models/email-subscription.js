var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var emailSubscriptionSchema = new Schema({
  email: {type: String, trim: true}
});

module.exports = mongoose.model('EmailSubscription', emailSubscriptionSchema);
