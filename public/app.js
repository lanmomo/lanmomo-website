'use strict';
var TICKET_TYPES = {PC: 0, CONSOLE: 1};

var TICKET_TYPES_STR = {0: 'BYOC', 1: 'Console'};

var app = angular.module('App', ['angular-loading-bar', 'ngAnimate', 'ngRoute', 'ui.bootstrap', 'angularMoment', 'ngCookies', 'ja.qr'])
  .directive('passwordCheck', [function () {
        return {
          restrict: 'A',
          scope: true,
          require: 'ngModel',
          link: function (scope, elem , attributes, control) {
            var checker = function () {
              var password1 = scope.$eval(attributes.ngModel);
              var password2 = scope.$eval(attributes.passwordCheck);
              return password1 == password2;
            };
            scope.$watch(checker, function (n) {
              control.$setValidity('unique', n);
            });
          }
        }
      }
    ]).factory('Auth', function($rootScope, $http) {
      return {
        login : function() {
          $rootScope.loggedIn = true;
          $rootScope.$broadcast('login');
        },
        isLoggedIn : function() {
          return $rootScope.loggedIn;
        },
        logout : function() {
          $rootScope.loggedIn = false;
          $rootScope.$broadcast('login');
        },
        refresh: function() {
          $http.get('/api/login')
            .success(function(data) {
              if (data.logged_in) {
                Auth.login();
              } else {
                $rootScope.loggedIn = false;
              }
            })
            .error(function(err, status) {
              $rootScope.loggedIn = false;
            });
        }
      }
    });

app.run(function($rootScope, $http, Auth) {
  // runs on first page load or refresh
  $http.get('/api/login')
    .success(function(data) {
      $rootScope.loggedIn = data.logged_in;
    })
    .error(function(err, status) {
      $rootScope.loggedIn = false;
    });
});

app.controller('NavbarController', function($scope, $location, Auth) {
  $scope.isActive = function(url) {
    return $location.path() === url;
  };

  $scope.refresh = function () {
    $scope.loggedIn = Auth.isLoggedIn();
  };

  $scope.$on('login', function() {
    $scope.refresh();
  });

  $('.navbar-nav li a').click(function() {
    if ($('.navbar-collapse.collapse').hasClass('in')) {
      $('#navbar').collapse('hide');
    }
  });
});

app.controller('GamesController', function($scope, $http) {
  $http.get('/api/games')
    .success(function(games) {
      $scope.games = games;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
});

app.controller('TournamentsController', function($scope, $http, $location) {
  function refreshData() {
    $http.get('/api/tournaments')
      .success(function(data) {
        $scope.tournaments = data.tournaments;
      })
      .error(function(err, status) {
        $scope.error = {message: err, status: status};
      });

      $http.get('/api/teams')
        .success(function(data) {
          $scope.teams = data.teams;
        })
        .error(function(err, status) {
          $scope.error = {message: err.error, status: status};
        });

      if ($scope.loggedIn) {
        $http.get('/api/profile')
        .success(function(data) {
          $scope.user = data.user;
        })
        .error(function(err, status) {
          $scope.error = {message: err.error, status: status};
        });
      }
  }

  $scope.createTeam = function(_name, _game) {
    var data = {
      game: _game,
      name: _name
    };
    $http.post('/api/teams',data)
      .success(function(data) {
        refreshData();
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.deleteTeam = function(id, index) {
    if (confirm('Êtes vous certain de vouloir supprimer cette équipe ?')) {
      $http.delete('/api/teams/' + id)
        .success(function(data) {
          $scope.teams.splice(index, 1);
        })
        .error(function(err, status) {
          $scope.error = {message: err.error, status: status};
        });
    }
  };

  refreshData();
});

app.controller('ServersController', function($scope, $http, $interval) {
  $scope.state = {
    loading: true
  };
  $scope.refresh = function() {
    $http.get('/api/servers')
      .success(function(servers) {
        $scope.servers = servers;
        $scope.state.loading = false;
      })
      .error(function(err, status) {
        $scope.error = {message: err, status: status};
        $scope.state.loading = false;
      });
  };
  $scope.isEmpty = function(obj) {
    for (var key in obj) {
      if (obj.hasOwnProperty(key)) {
        return false;
      }
    }
    return true;
  };
  $scope.refresh();
  $scope.intervalPromise = $interval(function() {
    $scope.refresh();
  }, 10000);
  $scope.$on('$destroy', function() {
    $interval.cancel($scope.intervalPromise);
  });
});

app.controller('TicketsController', function($scope, $http, $location) {
  $scope.max = {
    pc: 96,
    console: 32
  };

  var ticketCounts = {
    'temp': {0: 0, 1: 0},
    'paid': {0: 0, 1: 0}
  };
  $http.get('/api/tickets')
    .success(function(data) {
      var tickets = data.tickets;

      for (var i = 0; i < tickets.length; i++) {
        var ticket = tickets[i];
        var count = ticketCounts['temp'];
        if (ticket.paid) {
          count = ticketCounts['paid'];
        }
        count[ticket.type_id]++;
      }
      $scope.ticketCount = {
        pc: {
          real: ticketCounts['paid'][0],
          temp: ticketCounts['temp'][0],
          total: ticketCounts['paid'][0] + ticketCounts['temp'][0]
        },
        console: {
          real: ticketCounts['paid'][1],
          temp: ticketCounts['temp'][1],
          total: ticketCounts['paid'][1] + ticketCounts['temp'][1]
        }
      };
    })
    .error(function(err, status) {
      $scope.error = {message: err.error, status: status};
    });

  $scope.buy = function(ticketType) {
    var ticket = {};
    $scope.submitted = true;
    ticket.type = ticketType;

    if (ticketType === TICKET_TYPES.CONSOLE) {
      $http.post('/api/tickets', ticket)
        .success(function(data) {
          $location.path('/pay');
        })
        .error(function(err, status) {
          $scope.error = err.error;
        });
    } else if (ticketType === TICKET_TYPES.PC) {
      $location.path('/map');
    } else {
      console.log('wrong type id');
    }
  };
});

app.controller('PayController', function($scope, $http, $window) {
  $http.get('/api/users/ticket')
    .success(function(data) {
      $scope.ticket = data.ticket;
      $scope.ticket_type_str = TICKET_TYPES_STR[data.ticket.type_id];
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });

  $scope.getTotal = function () {
    if (!$scope.ticket) {
      return 0;
    }
    if ($scope.discountMomo) {
      return $scope.ticket.price - 5;
    }
    return $scope.ticket.price;
  };

  $scope.payNow = function () {
    var data = {};
    data.discount_momo = $scope.discountMomo;

    $http.post('/api/tickets/pay', data)
      .success(function(data) {
        $window.location.href = data.redirect_url;
      })
      .error(function(err, status) {
        $scope.error = {message: err, status: status};
      });
  }
});

app.controller('VerifyController', function($scope, $http, $routeParams) {
  var token = $routeParams.token;

  $http.get('/api/verify/' + token)
    .success(function(data, status) {
      if (data.first) {
        $scope.message = 'Votre compte a bien été créé ! Vous pouvez maintenant vous connecter.';
      } else if (data.first === false) {
        $scope.message = 'Votre compte a déjà été créé ! Vous pouvez vous connecter.';
      } else {
        $scope.error = 'Une erreur est survenue lors de la confirmation de votre compte. Veuillez contacter info@lanmomo.org !'
      }
    })
    .error(function(data) {
      $scope.error = 'Une erreur est survenue lors de la confirmation de votre compte. Veuillez contacter info@lanmomo.org !'
    });
});

app.controller('LoginController', function ($scope, $http, $location, $rootScope, Auth) {
  $scope.submitLogin = function () {
    var data = {
        email: $scope.user.email,
        password: $scope.user.password
    };
    $http.post('/api/login', data)
      .success(function(data) {
        Auth.login();
        $location.path('/profile');
      })
      .error(function(err, status) {
        $scope.error = {message: err.error, status: status};
      });
  };
});

app.controller('LogoutController', function ($scope, $http, $location, Auth) {
  $http.get('/api/logout')
    .success(function(data) {
      Auth.logout();
      $location.path('/');
    })
    .error(function(err, status) {
      $scope.error = {message: err.error, status: status};
    });
});

app.controller('ExecuteController', function ($scope, $http, $location, $routeParams) {
  var data = {
    'payment_id' : $routeParams.paymentId,
    'payer_id' : $routeParams.PayerID
  };

  $http.put('/api/tickets/pay/execute', data)
    .success(function(data) {
      console.log(data);
      $scope.message = data.message;
    })
    .error(function(err, status) {
      console.log(err);
      $scope.error = {message: err.error, status: status};
    });
});

app.controller('ProfileController', function ($scope, $http) {
  $scope.alerts= [];
  $scope.state = {
    submitted: false,
    loading: false,
    success: false,
    error: false,
    usernameChanged: false,
    emailChanged: false,
    usernameAvailable: false,
    emailAvailable: false,
  };

  $http.get('/api/profile')
    .success(function(data) {
      $scope.userData = data.user;
      $scope.formUser = angular.copy($scope.userData);
      $scope.resetMods();
    })
    .error(function(err, status) {
      $scope.error = {message: err.error, status: status};
    });
  $http.get('/api/users/ticket')
    .success(function(data) {
      if (data.ticket) {
        $scope.userTicket = data.ticket;
        $scope.qrCodeString = 'https://lanmomo.org/qr/' + data.ticket.qr_token;
      }
    })
    .error(function(err, status) {
      $scope.alerts.push({msg: err.error, type: 'danger'});
    });

    $scope.submitUserMods = function () {
      $http.put('/api/users', $scope.formUser)
        .success(function(data) {
          $scope.userData = data.user;
          $scope.resetMods();
          $scope.alerts.push({msg: 'Vos informations ont été mises à jour.', type: 'success'});
        })
        .error(function(err, status) {
          $scope.alerts.push({msg: err.error, type: 'danger'});
        });
    }

    $scope.resetMods = function () {
      $scope.edit = false;
      $scope.formUser = angular.copy($scope.userData);
      $scope.state.emailAvailable = true;
      $scope.state.emailChanged = true;
      $scope.state.usernameAvailable = true;
      $scope.state.usernameChanged = true;
    }

    $scope.isUsernameAvailable = function(user) {
      if (user.username == $scope.userData.username){
        $scope.state.usernameAvailable = true;
        $scope.state.usernameChanged = true;
        return;
      }
      $http.post('/api/users/has/username', {username: user.username})
        .success(function(data) {
          $scope.state.usernameAvailable = !data.exists;
          $scope.state.usernameChanged = true;
        })
        .error(function(data) {
          $scope.state.usernameAvailable = false;
          $scope.state.usernameChanged = true;
        });
    };
    $scope.resetUsernameChanged = function() {
      $scope.state.usernameChanged = false;
    };
    $scope.isEmailAvailable = function(user) {
      if (user.email == $scope.userData.email){
        $scope.state.emailAvailable = true;
        $scope.state.emailChanged = true;
        return;
      }
      $http.post('/api/users/has/email', {email: user.email})
        .success(function(data) {
          $scope.state.emailAvailable = !data.exists;
          $scope.state.emailChanged = true;
        })
        .error(function(data) {
          $scope.state.emailAvailable = false;
          $scope.state.emailChanged = true;
        });
    };
    $scope.resetEmailChanged = function() {
      $scope.state.emailChanged = false;
    };
});

app.controller('QRController', function ($scope, $http, $routeParams) {
  var token = $routeParams.token;
  $scope.ticketTypes = TICKET_TYPES_STR;

  $http.get('/api/qr/' + token)
    .success(function(data) {
      if (data.ticket && data.owner) {
        $scope.ticket = data.ticket;
        $scope.owner = data.owner;
      }
    })
    .error(function(err, status) {
      $scope.error = {message: err.error, status: status};
    });
});


app.controller('SignupController', function($scope, $http) {
  $('[data-toggle="tooltip"]').tooltip();
  $scope.state = {
    submitted: false,
    loading: false,
    success: false,
    error: false,
    usernameChanged: false,
    emailChanged: false,
    usernameAvailable: false,
    emailAvailable: false,
  };
  $scope.signup = function(data) {
    $scope.state.loading = true;
    $scope.state.submitted = true;
    $http.post('/api/users', data)
      .success(function(res, status) {
        $scope.message = res.message;
        $scope.state.loading = false;
        $scope.state.success = true;
      })
      .error(function(data) {
        $scope.message = 'Malheureusement, une erreur est survenue lors de votre inscription !' +
          ' Veuillez réessayer plus tard et contacter info@lanmomo.org si le problème persiste.';
        $scope.state.loading = false;
        $scope.state.error = true;
      });
  };
  $scope.isUsernameAvailable = function(user) {
    $http.post('/api/users/has/username', {username: user.username})
      .success(function(data) {
        $scope.state.usernameAvailable = !data.exists;
        $scope.state.usernameChanged = true;
      })
      .error(function(data) {
        $scope.state.usernameAvailable = false;
        $scope.state.usernameChanged = true;
      });
  };
  $scope.resetUsernameChanged = function() {
    $scope.state.usernameChanged = false;
  };
  $scope.isEmailAvailable = function(user) {
    $http.post('/api/users/has/email', {email: user.email})
      .success(function(data) {
        $scope.state.emailAvailable = !data.exists;
        $scope.state.emailChanged = true;
      })
      .error(function(data) {
        console.log(data);
        $scope.state.emailAvailable = false;
        $scope.state.emailChanged = true;
      });
  };
  $scope.resetEmailChanged = function() {
    $scope.state.emailChanged = false;
  };
});

app.controller('MapController', function ($scope, $http, $interval, $location) {
  $scope.selectedSeat = null;
  var seatStatus = {};
  var seatOwners = {};
  refresh();

  var refreshInterval = $interval(function () {
      refresh();
  }, 5000);

  $scope.$on('$destroy', function () {
    $interval.cancel(refreshInterval);
  });

  $scope.buy = function(seatNum) {
    var ticket = {};
    $scope.submitted = true;
    ticket.type = TICKET_TYPES.PC;
    ticket.seat = seatNum;

    $http.post('/api/tickets', ticket)
      .success(function(data) {
        $location.path('/pay');
      })
      .error(function(err, status) {
        $scope.error = err.error;
      });
  };

  function refresh() {
    $http.get('/api/tickets/type/0')
      .success(function(data) {
        seatStatus = {};
        seatOwners = {};
        var tickets = data.tickets;
        for (var i = 0; i < tickets.length; i++) {
          var seat_num = tickets[i].seat_num;
          if (tickets[i].paid) {
            seatStatus[seat_num] = 't';
          } else {
            seatStatus[seat_num] = 'r';
          }
          seatOwners[seat_num] = tickets[i].owner_username;
        }
        // TODO check if selectedSeatTicket is updated !
      })
      .error(function(err, status) {
        $scope.error = {message: err.error, status: status};
      });
  }
  function resetSelectedSeat() {
    delete $scope.selectedSeatTicket;
    delete $scope.selectedSeatUser;
    delete $scope.error;
    delete $scope.selectSeatIsFree;
  }

  $scope.isAvail = function (seat) {
    return !seatStatus.hasOwnProperty(seat);
  };
  $scope.isReserved = function (seat) {
    return seatStatus[seat] == 'r';
  };
  $scope.isTaken = function (seat) {
    return seatStatus[seat] == 't';
  };
  $scope.getOwner = function (seat) {
    return seatOwners[seat];
  };
  $scope.selectSeat = function (seat) {
    $http.get('/api/tickets/seat/' + seat + '/free')
      .success(function(data) {
        resetSelectedSeat();
        $scope.selectedSeatID = seat;
        if (!data.free) {
          $scope.error = 'siège occupé par ' + data.user.username;
          $scope.selectedSeatTicket = data.ticket;
          $scope.selectedSeatUser = data.user;
        } else {
          $scope.selectSeatIsFree = true;
        }
      })
      .error(function(err, status) {
        resetSelectedSeat();
        $scope.error = {message: err.error, status: status};
      });

  };
  $scope.times = function (x) {
    return new Array(x);
  };
});

app.config(function($routeProvider, $locationProvider, cfpLoadingBarProvider) {
  $routeProvider.when('/', {
    templateUrl: 'partials/home.html'
  })
  .when('/tickets', {
    templateUrl: 'partials/tickets.html',
    controller: 'TicketsController'
  })
  .when('/pay', {
    templateUrl: 'partials/pay.html',
    controller: 'PayController'
  })
  .when('/pay/execute', {
    templateUrl: 'partials/execute.html',
    controller: 'ExecuteController'
  })
  .when('/map', {
    templateUrl: 'partials/map.html',
    controller: 'MapController'
  })
  .when('/games', {
    templateUrl: 'partials/games.html',
    controller: 'GamesController'
  })
  .when('/tournaments', {
    templateUrl: 'partials/tournaments.html',
    controller: 'TournamentsController'
  })
  .when('/servers', {
    templateUrl: 'partials/servers.html',
    controller: 'ServersController'
  })
  .when('/about', {
    templateUrl: 'partials/about.html'
  })
  .when('/terms', {
    templateUrl: 'partials/terms.html'
  })
  .when('/faq', {
    templateUrl: 'partials/faq.html'
  })
  .when('/contact', {
    templateUrl: 'partials/contact.html'
  })
  .when('/signup', {
    templateUrl: 'partials/signup.html',
    controller: 'SignupController'
  })
  .when('/profile', {
    templateUrl: 'partials/profile.html',
    controller: 'ProfileController'
  })
  .when('/login', {
    templateUrl: 'partials/login.html',
    controller: 'LoginController'
  })
  .when('/logout', {
    templateUrl: 'partials/home.html',
    controller: 'LogoutController'
  })
  .when('/verify/:token', {
    templateUrl: 'partials/verify.html',
    controller: 'VerifyController'
  })
  .when('/qr/:token', {
    templateUrl: 'partials/qr.html',
    controller: 'QRController'
  });

  $routeProvider.otherwise({redirectTo: '/'});

  $locationProvider.html5Mode(true);

  cfpLoadingBarProvider.includeSpinner = false;

  moment.locale('fr-ca');
});

app.filter('capitalize', function() {
  return function(input) {
    return input.substring(0, 1).toUpperCase() + input.substring(1);
  };
});
