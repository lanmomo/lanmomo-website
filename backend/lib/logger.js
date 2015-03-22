var log4js = require('log4js');

var config = require('./../config/config');

var layout = log4js.layouts.layout('pattern', config.logger.layout);
var console = log4js.appenders.console(layout);

log4js.configure({}); // Resetting default configuration
log4js.addAppender(console);
log4js.setGlobalLogLevel(config.logger.level);

var logger = log4js.getLogger();

module.exports = logger;
