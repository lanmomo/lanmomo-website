module.exports = {
  server: {
    hostname: 'localhost',
    port: 3000
  },
  url: {
    root: 'http://localhost:3000'
  },
  mailer: {
    from: {
      name: 'LAN Montmorency',
      address: 'user@gmail.com'
    },
    transportOptions: {
      host: 'smtp.gmail.com',
      port: 465,
      secure: true,
      authMethod: 'LOGIN',
      auth: {
        user: 'user@gmail.com',
        pass: 'password'
      }
    }
  },
  db: {
    url: 'mongodb://localhost/dev'
  },
  maximum: 50,
  games: [{
    title: 'Team Fortress 2',
    description: 'PVP et Mann Versus Machine',
    imagePath: 'assets/game_banners/tf2.jpg'
  }],
  token: 'token',
};
