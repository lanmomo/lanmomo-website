var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var gameSchema = new Schema({
  game_id:String,
  title: String,
  description: String,
  imagePath: String
});

module.exports = mongoose.model('Game', gameSchema);
