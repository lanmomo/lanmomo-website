var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var userSchema = new Schema({
  username: {type: String, trim: true},
  firstname: {type: String, trim: true},
  lastname: {type: String, trim: true},
  email: {type: String, trim: true},
  phone: {type: String, trim: true},
  type: {type: String, trim: true},
  active: Boolean
});

module.exports = mongoose.model('User', userSchema);
