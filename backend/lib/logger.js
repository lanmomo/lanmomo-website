var winston = require('winston');
var moment = require('moment');

var config = require('./../config/config');

var logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)({
      level: config.logger.level,
      timestamp: function () {
        return moment().format('HH:mm:ss,SSS');
      },
      // Format: TIMESTAMP [LEVEL] MESSAGE META
      formatter: function(options) {
        return options.timestamp() + ' [' + options.level.toUpperCase() + '] ' +
               (undefined !== options.message ? options.message : '') +
               (options.meta && Object.keys(options.meta).length ? '\n\t' + JSON.stringify(options.meta) : '');
      }
    })
  ]
});

module.exports = logger;
