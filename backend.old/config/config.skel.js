module.exports = {
  db: {
    url: 'mongodb://localhost/lanmomo'
  },
  notifier: {
    token: 'abc123'
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
  logger: {
    level: 'debug',
    layout: {
      pattern: '%d{ABSOLUTE} %[[%p]%] %m'
    }
  }
};
