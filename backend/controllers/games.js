var Game = require('../models/game.js');

exports.getAll = function (req, res) {
  Game.find().select('title description imagePath').exec()
  .then(function (games) {
    res.status(200).json(games);
  })
  .reject(function (err) {
    console.log(err);
    res.status(500).json({message:"Une erreur s'est produite lors de la recherche des jeux"});
  });
};
