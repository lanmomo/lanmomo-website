var config = require('../config/config');
var logger = require('../lib/logger');
var moment = require('moment');

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

exports.updateServers = function updateServers(req, res) {
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

exports.getAll = function getAll(req, res) {
  res.status(200).json(servers);
};

exports.purgeTimer = function purgeTimer() {
  setInterval(function() {
    try {
      var limit = moment().subtract(5, 'minutes'); // Five minutes ago
      for (var key in servers) {
        if (servers.hasOwnProperty(key)) {
          var server = servers[key];
          if (limit.isAfter(server.lastUpdate)) {
            logger.debug('Removing server from list: %s', server.hostname);
            delete servers[server.hostname];
          }
        }
      }
    } catch (err) {
      logger.error('Error occurred while running purgeTimer:', err);
    }
  }, 60000); // One minute
};
