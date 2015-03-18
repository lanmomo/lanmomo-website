var winston = require('winston');

var config = require('./../config/config');

var logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)({
      level: config.logger.level,
      // Timestamp: HH:mm:ss,SSS
      timestamp: function () {
        function format(str, length) {
          length = length || 2;
          length = 0 - length;
          return String('00' + str).slice(length);
        }
        var date = new Date();
        return format(date.getHours()) + ':' + format(date.getMinutes()) + ':' + format(date.getSeconds()) + ',' + format(date.getMilliseconds(), 3);
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
