var usersController = require('../controllers/users');

module.exports = function(app) {
  //TODO in mainController
  app.get('/', usersController.index);
  app.get('/api/users', usersController.getAll);
  app.post('/api/subscribe', usersController.subscribe);
  app.get('/api/verify/:emailId', usersController.verify);
};
