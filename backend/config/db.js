var db = {};
//TODO Common configuration
switch(process.env.NODE_ENV) {
  case 'dev':
    db = {url: 'mongodb://localhost/dev'};
    break;
  case 'prod':
    //TODO Add security
    db = {url: 'mongodb://localhost/lanmomo'};
    break;
}

module.exports = db;
