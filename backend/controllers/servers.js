var config = require('../config/config');
var logger = require('../lib/logger');

var servers = {};

var createServer = function(server) {
  return {
    game: {
      id: server.game,
      name: config.servers.games[server.game]
    },
    hostname: server.hostname,
    ip: server.ip,
    lastUpdate: Date.now()
  };
};

exports.updateServers = function(req, res) {
  logger.debug('Received update request', req.body);
  var server = req.body;
  var token = req.body.token;
  if (token && token === config.notifier.token) {
    servers[server.hostname] = createServer(server);
    logger.debug('Updated server entry: %s', server.hostname, servers[server.hostname]);
    res.status(200).json({message: "Success", data: servers});
  } else {
    logger.warn('Invalid token: %s', token);
    res.status(403).json({message: "Failure, wrong token"});
  }
};

exports.getAll = function(req, res) {
  res.status(200).json(servers);
};
