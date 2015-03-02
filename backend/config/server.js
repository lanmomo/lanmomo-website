var server = {};
switch(process.env.NODE_ENV) {
  case 'dev':
    server = {port: 3000};
    break;
  case 'prod':
    server = {port: 80};
    break;
}

module.exports = server;
