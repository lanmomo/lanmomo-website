var mainController = require('../controllers/main');
var usersController = require('../controllers/users');
var gamesController = require('../controllers/games');
var serversController = require('../controllers/servers');
var logger = require('../lib/logger');

module.exports = function(app) {
  logger.info('Initializing routes');

  app.get(/^\/(users|games|about|rules|contact|subscribe|congratulations)?$/, mainController.index);
  app.get('/api/users', usersController.getAll);
  app.get('/api/users/max/:type', usersController.getMax);
  app.post('/api/subscribe', usersController.subscribe);
  app.get('/api/verify/:emailId', usersController.verify);
  app.get('/api/games', gamesController.getAll);
  app.get('/api/servers', serversController.getServers);
  app.post('/api/servers', serversController.updateServers);
};
