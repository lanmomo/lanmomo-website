var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var userSchema = new Schema({
  username: String,
  firstname: String,
  lastname: String,
  email: String,
  phone: String,
  console: Boolean,
  active: Boolean
});

module.exports = mongoose.model('User', userSchema);
