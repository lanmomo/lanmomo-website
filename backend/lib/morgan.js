var morgan = require('morgan');

var logger = require('./logger');

var wrappedMorgan = morgan(
  'dev', {
    stream: {
      write: function(str) {
        logger.info(str.slice(0, -1)); // We slice to remove the `\n` added by morgan
      }
    }
  }
);

module.exports = wrappedMorgan;
