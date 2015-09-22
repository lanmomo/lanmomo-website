var config = require('../config/config');

exports.getAll = function getAll(req, res) {
  if (config.games) {
    res.status(200).json(config.games);
  } else {
    res.status(500).json({message: "no games"});
  }
};
