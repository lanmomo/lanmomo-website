var db = {};
switch(process.env.NODE_ENV) {
  case 'dev':
    db = {url: 'mongodb://localhost/dev'}
  case 'prod':
    db = {url: 'mongodb://localhost/lanmomo'}
}

module.exports = db;
