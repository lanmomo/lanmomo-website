var mainController = require('../controllers/main');
var usersController = require('../controllers/users');

module.exports = function(app) {
  app.get('/', mainController.index);
  app.get('/api/users', usersController.getAll);
  app.post('/api/subscribe', usersController.subscribe);
  app.get('/api/verify/:emailId', usersController.verify);
};
