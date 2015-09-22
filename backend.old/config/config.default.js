module.exports = {
  server: {
    port: 3000
  },
  url: {
    root: 'http://localhost:3000'
  },
  db: {
    url: 'mongodb://localhost/lanmomo'
  },
  notifier: {
    token: 'abc123'
  },
  mailer: {
    from: {
      name: 'LAN Montmorency',
      address: 'root@localhost'
    },
    transportOptions: {
      host: 'localhost',
      port: 25
    }
  },
  logger: {
    level: 'info',
    layout: {
      pattern: '%d{ABSOLUTE} [%p] %m'
    }
  },
  types: ['pc', 'console'],
  maximum: {
    pc: 50,
    console: 15
  },
  servers: {
    games: {
      csgo: 'Counter Strike: Global Offensive',
      'csgo-gg': 'CS:GO: Arms race',
      'csgo-comp': 'CS:GO: Competitive',
      css: 'Counter Strike: Source',
      kf: 'Killing Floor',
      mumble: 'Serveur mumble pour les jeux',
      mc: 'Minecraft',
      mvm: 'TF2: Mann vs. Machine',
      ph: 'TF2: Prop Hunt',
      tf2: 'Team Fortress 2',
      ttt: 'Garry\'s Mod: Trouble in Terrorist Town',
      tmnf: 'TrackMania Nations Forever',
      ut2004: 'Unreal Tournament 2004'
    }
  },
  games: {
    pc: [
      {
        title: 'Team Fortress 2',
        description: 'FPS multijoueur développé par Valve. Les modes de jeux PVP et Mann Versus Machine seront offerts.',
        imagePath: 'assets/game_banners/tf2.jpg'
      },
      {
        title: 'Counter Strike: Source',
        description: 'FPS en équipe développé par Valve. Les modes poser la bombe et délivrer les otages seront offert.',
        imagePath: 'assets/game_banners/css.jpg'
      },
      {
        title: 'CS: Global Offensive',
        description: 'FPS en équipe développé par Valve. Les modes poser la bombe et délivrer les otages seront offert.',
        imagePath: 'assets/game_banners/csgo.jpg'
      },
      {
        title: 'Minecraft',
        description: 'Sandbox multijoueur développé par Mojang. Une course au dragon coopérative en mode survie sera organisée.',
        imagePath: 'assets/game_banners/minecraft.jpg'
      },
      {
        title: 'Garry\'s Mod',
        description: 'Sandbox multijoueur développé par Facepunch Studios. Les modes Trouble in Terrorist Town et Prop Hunt sont prévus.',
        imagePath: 'assets/game_banners/gmod.jpg'
      },
      {
        title: 'TrackMania Nations Forever',
        description: 'Jeu de course multijoueur développé par Nadeo.',
        imagePath: 'assets/game_banners/tmnations.jpg'
      },
      {
        title: 'Killing Floor',
        description: 'FPS multijoueur coopératif développé par Tripwire Interactive où vous devez éliminer des hordes de zombies.',
        imagePath: 'assets/game_banners/kf.jpg'
      },
      {
        title: 'Unreal Tournament 2004',
        description: 'FPS futuriste développé par Epic Games et Digital Extremes.',
        imagePath: 'assets/game_banners/ut2004.jpg'
      },
      {
        title: 'Hearthstone',
        description: 'Hearthstone: Heroes of Warcraft est un jeu de cartes à collectionner en ligne, édité et développé par Blizzard Entertainment.',
        imagePath: 'assets/game_banners/hs.jpg'
      },
      {
        title: 'League of Legends',
        description: 'Arène de bataille multijoueur développée par Riot Games.',
        imagePath: 'assets/game_banners/lol.jpg'
      },
      {
        title: 'Rocket League',
        description: 'Rocket League est un mélange de jeu de voiture et de jeu de soccer développé par Psyonix.',
        imagePath: 'assets/game_banners/rl.jpg'
      }
    ],
    console: [
      {
        title: 'TowerFall',
        description: 'Jeux de combat en arène développé par Matt Thorson dans lequel les joueurs  s\'affrontent à l\'aide de flèches et de sauts sur la tête.',
        imagePath: 'assets/game_banners/towerfall.jpg'
      },
      {
        title: 'Super Smash Bros. Melee',
        description: 'Jeu de combat populaire développé par Nintendo mettant en vedette des personnages provenant de divers jeux vidéos.',
        imagePath: 'assets/game_banners/melee.jpg'
      },
      {
        title: 'ProjectM',
        description: 'Mod du jeu de combat Super Smash Bros. Brawl, conçu pour ressembler au style de combat du jeu de la même série: Super Smash Bros. Melee.',
        imagePath: 'assets/game_banners/projectM.jpg'
      }
    ]
  }
};
