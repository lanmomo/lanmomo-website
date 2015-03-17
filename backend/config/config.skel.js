module.exports = {
  server: {
    hostname: 'localhost',
    port: 3000
  },
  mail: {
    user: 'username@gmail.com',
    password: 'lelthisisapassword'
  },
  db: {
    url: 'mongodb://localhost/dev'
  },
  maximum: 50,
  games: [{
    title: 'Team Fortress 2',
    description: 'PVP et Mann Versus Machine',
    imagePath: 'assets/game_banners/tf2.jpg'
  }]
};
