var servers = {};
var config = require('../config/config');

exports.updateServers = function(req, res) {
  var server = req.body;
  var token = req.get("Notifier-Token");
  if (token && token === config.notifier.token) {
    servers[server.hostname] = server;
    res.status(200).json({message: "Success", data: servers});
  } else {
    res.status(403).json({message: "Failure, wrong token"});
  }
};

exports.getServers = function(req, res) {
  res.status(200).json(servers);
};
