var db = {};
switch(process.env.NODE_ENV) {
  case 'dev':
    db = {url: 'mongodb://localhost/dev'};
    break;
  case 'prod':
    db = {url: 'mongodb://localhost/lanmomo'};
    break;
}

module.exports = db;
