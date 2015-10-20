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
  }])
  .factory('Auth', function($rootScope, $http) {
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
        var _this = this;

        $http.get('/api/login')
          .success(function(data, status, headers) {
            $rootScope.commit = headers().commit;
            if (data.logged_in) {
              _this.login();
            } else {
              $rootScope.loggedIn = false;
            }
          })
          .error(function() {
            $rootScope.loggedIn = false;
          });
      }
    }
  })
  .factory('Timer', function($rootScope, $interval) {
    return {
      intervalPromise: null,
      timestamp_until: null,
      diff: null,
      /**
       * Timer bootstrap method.
       *
       * To setup and initiate the Timer, call:
       *
       *     Timer.bootstrap($scope, datetime);
       *
       * @param {Scope} $scope Current scope where the Timer is being bootstrap.
       * @param {Date} datetime Date object or string representing a date.
       *
       */
      bootstrap: function($scope, datetime_now, datetime_until) {
        this.cleanup();
        this.timestamp_until = moment(datetime_until).valueOf();
        var timestamp_now = moment(datetime_now).valueOf();
        this.diff = timestamp_now - Date.now();

        this.intervalPromise = $interval(function() {
          this.refresh();
        }.bind(this), 100);

        $scope.$on('$destroy', function() {
          this.cleanup();
        }.bind(this));
      },
      refresh: function() {
        var date = this.timestamp_until - (Date.now() + this.diff);

        if (date < 1) {
            $interval.cancel(this.intervalPromise);
            return;
        }

        var minutes = Math.floor(date % 3600000 / 60000);
        var seconds = Math.floor(date % 60000 / 1000);
        seconds = String("00" + seconds).slice(-2);

        $rootScope.timerTime = minutes + ':' + seconds;

        if (minutes < 1) {
          $rootScope.timerTimeDanger = true;
        }
      },
      cleanup: function() {
        $rootScope.timerTime = null;
        $rootScope.timerTimeDanger = null;

        if (this.intervalPromise) {
          $interval.cancel(this.intervalPromise);
        }

        this.intervalPromise = null;
        this.timestamp_until = null;
        this.diff = null;
      }
    };
  });

app.run(function($rootScope, $http, Auth) {
  // runs on first page load and refresh
  Auth.refresh();
});

app.controller('NavbarController', function($scope, $location, Auth) {
  $scope.isActive = function(url) {
    return $location.path() === url;
  };

  $scope.refresh = function() {
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

app.controller('HomeController', function($scope, $http, Auth) {
  $scope.hasTicket = false;

  $scope.init = function() {
    if (Auth.isLoggedIn()) {
      $http.get('/api/users/ticket')
        .success(function (data) {
          $scope.hasTicket = $scope.loggedIn && data.ticket && data.ticket.paid;
        })
        .error(function (err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.init();
  $scope.$on('login', function() {
    $scope.init();
  });
});

app.controller('GamesController', function($scope, $http) {
  $http.get('/assets/games.json')
    .success(function(games) {
      $scope.games = games;
    })
    .error(function(err, status) {
      $scope.error = {message: err.message, status: status};
    });
});

app.controller('TournamentsController', function($scope, $http, $modal, Auth) {
  $scope.hasTicket = false;

  $scope.init = function() {
    $http.get('/assets/tournaments.json')
      .success(function(data) {
        $scope.tournaments = data.tournaments;
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });

    if (Auth.isLoggedIn()) {
      $http.get('/api/users/ticket')
        .success(function (data) {
          $scope.ticket = data.ticket;
          $scope.hasTicket = $scope.loggedIn && $scope.ticket && $scope.ticket.paid;
        })
        .error(function(err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.refresh = function() {
    $http.get('/api/teams')
      .success(function(data) {
        $scope.teams = data.teams;
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });

    $http.get('/api/team_users')
      .success(function(data) {
        $scope.team_users = data.team_users;
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.init();
  $scope.refresh();
  $scope.$on('login', function() {
    $scope.init();
  });

  $scope.isSingle = function(tournament) {
    return tournament.team_size == 1;
  };
  $scope.isTeam = function(tournament) {
    return tournament.team_size != 1;
  };
  $scope.isMember = function(team_user) {
    return $scope.ticket && $scope.ticket.owner_username == team_user.username;
  };
  $scope.isCaptain = function(team) {
    return $scope.ticket && $scope.ticket.owner_username == team.captain_name;
  };

  $scope.createTeam = function(name, game) {
    var data = {
      game: game,
      name: name
    };

    $http.post('/api/teams',data)
      .success(function() {
        $scope.refresh();
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.deleteTeam = function(id, index) {
    if (confirm('Êtes vous certain de vouloir supprimer cette équipe ?')) {
      $http.delete('/api/teams/' + id)
        .success(function() {
          $scope.teams.splice(index, 1);
        })
        .error(function(err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.deleteTeamUser = function(id, index) {
    if (confirm('Êtes vous certain de vouloir retirer cette personne ?')) {
      $http.delete('/api/team_users/' + id)
        .success(function() {
          $scope.team_users.splice(index, 1);
        })
        .error(function(err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.joinTourney = function(game) {
    var name = Math.random().toString(36).replace(/[^a-zA-Z0-9]+/g, '').substr(0, 26);
    $scope.createTeam(name, game);
  };

  $scope.joinTeam = function(id, game) {
    var data = {
      team_id: id,
      game: game
    };

    $http.post('/api/team_users', data)
      .success(function() {
        $scope.refresh();
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.modal = function(game) {
    var modalInstance = $modal.open({
      controller: 'TournamentsModalController',
      templateUrl: 'partials/tournaments-modal.html'
    });
    modalInstance.result.then(function(name) {
      if (name) {
        $scope.createTeam(name, game);
      }
    });
  };
});

app.controller('TournamentsModalController', function($scope, $modalInstance) {
  $scope.ok = function() {
    $modalInstance.close($scope.name);
  };
  $scope.cancel = function() {
    $modalInstance.close();
  };
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
        $scope.error = {message: err.message, status: status};
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

app.controller('TicketsController', function($scope, $http, $location, $modal, Auth, Timer) {
  $scope.canBuy = false;
  $scope.ticket = null;
  $scope.submitted = false;
  $scope.max = {
    pc: 96,
    console: 32
  };
  var ticketCounts = {
    'temp': {0: 0, 1: 0},
    'paid': {0: 0, 1: 0}
  };

  $scope.init = function() {
    if (Auth.isLoggedIn()) {
      $http.get('/api/users/ticket')
        .success(function (data) {
          if (data.ticket && !data.ticket.paid && data.ticket.now && data.ticket.reserved_until) {
            Timer.bootstrap($scope, data.ticket.now, data.ticket.reserved_until);
          }
          $scope.canBuy = ($scope.loggedIn && !data.ticket) || ($scope.loggedIn && data.ticket && !data.ticket.paid);
          $scope.ticket = data.ticket;
        })
        .error(function (err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.init();
  $scope.$on('login', function() {
    $scope.init();
  });

  $scope.hasTicket = function(type) {
    return $scope.loggedIn && $scope.ticket && $scope.ticket.paid && $scope.ticket.type_id == type;
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
          total: ticketCounts['paid'][0] + ticketCounts['temp'][0],
          avail: $scope.max.pc - ticketCounts['paid'][0] - ticketCounts['temp'][0]
        },
        console: {
          real: ticketCounts['paid'][1],
          temp: ticketCounts['temp'][1],
          total: ticketCounts['paid'][1] + ticketCounts['temp'][1],
          avail: $scope.max.console - ticketCounts['paid'][1] - ticketCounts['temp'][1]
        }
      };
      $scope.ticketCount.pc.soldout = !($scope.ticketCount.pc.avail > 0);
      $scope.ticketCount.console.soldout = !($scope.ticketCount.console.avail > 0);
    })
    .error(function(err, status) {
      $scope.error = {message: err.message, status: status};
    });

  $scope.buy = function(type) {
    $scope.submitted = true;

    $http.get('/api/users/ticket')
      .success(function(data) {
        if (data.ticket) {
          if (data.ticket.type_id !== type) {
            $http.delete('/api/users/ticket')
              .success(function() {
                $scope.buyPart2(type);
              })
              .error(function(err, status) {
                $scope.error = {message: err.message, status: status};
              });
          } else {
            if (type === TICKET_TYPES.CONSOLE) {
              $location.path('/pay');
            } else if (type === TICKET_TYPES.PC) {
              $location.path('/map');
            } else {
              console.log('wrong type id');
            }
          }
        } else {
          $scope.buyPart2(type);
        }
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.buyPart2 = function(type) {
    var ticket = {};
    ticket.type = type;

    if (type === TICKET_TYPES.CONSOLE) {
      $http.post('/api/tickets', ticket)
        .success(function() {
          $location.path('/pay');
        })
        .error(function(err, status) {
          $scope.error = {message: err.message, status: status};
        });
    } else if (type === TICKET_TYPES.PC) {
      $location.path('/map');
    } else {
      console.log('wrong type id');
    }
  };

  $scope.modal = function() {
    $modal.open({
      controller: 'TicketsModalController',
      templateUrl: 'partials/tickets-modal.html'
    });
  };
});

app.controller('TicketsModalController', function($scope, $modalInstance, $location) {
  $scope.signup = function() {
    $modalInstance.close();
    $location.path('/signup');
  };
  $scope.login = function() {
    $modalInstance.close();
    $location.path('/login');
  };
});

app.controller('PayController', function($scope, $http, $window, $interval, Timer) {
  $scope.loading = false;

  $http.get('/api/users/ticket')
    .success(function(data) {
      if (data.ticket) {
        $scope.ticket = data.ticket;
        $scope.ticket_type_str = TICKET_TYPES_STR[data.ticket.type_id];
      } else {
        $scope.error = {message: 'Vous n\'avez sélectionné aucun billet.'};
      }
      if (data.ticket && !data.ticket.paid && data.ticket.now && data.ticket.reserved_until) {
        Timer.bootstrap($scope, data.ticket.now, data.ticket.reserved_until);
      }
    })
    .error(function(err, status) {
      $scope.error = {message: err.message, status: status};
    });

  $scope.getSeat = function() {
    if ($scope.ticket && $scope.ticket.seat_num) {
      return $scope.ticket.seat_num;
    } else {
      return '-';
    }
  };

  $scope.formatMoney = function(value) {
    return value + ',00$'
  };

  $scope.getTotal = function() {
    if (!$scope.ticket) {
      return 0;
    }
    if ($scope.discountMomo) {
      return $scope.ticket.price - 5;
    }
    return $scope.ticket.price;
  };

  $scope.payNow = function() {
    $scope.loading = true;

    var data = {
      discountMomo: $scope.discountMomo,
      participateGG: $scope.participateGG
    };

    $http.post('/api/tickets/pay', data)
      .success(function(data) {
        $window.location.href = data.redirect_url;
      })
      .error(function(err, status) {
        $scope.loading = false;
        $scope.error = {message: err.message, status: status};
      });
  }
});

app.controller('VerifyController', function($scope, $http, $routeParams) {
  var token = $routeParams.token;

  $http.get('/api/verify/' + token)
    .success(function(data) {
      if (data.first) {
        $scope.message = 'Votre compte a bien été créé ! Vous pouvez maintenant vous connecter.';
      } else if (data.first === false) {
        $scope.message = 'Votre compte a déjà été créé ! Vous pouvez vous connecter.';
      } else {
        $scope.error = {message: 'Une erreur est survenue lors de la confirmation de votre compte. Veuillez contacter info@lanmomo.org !'}
      }
    })
    .error(function() {
      $scope.error = {message: 'Une erreur est survenue lors de la confirmation de votre compte. Veuillez contacter info@lanmomo.org !'}
    });
});

app.controller('LoginController', function ($scope, $http, $location, $rootScope, Auth) {
  $scope.submitLogin = function () {
    var data = {
        email: $scope.user.email,
        password: $scope.user.password
    };
    $http.post('/api/login', data)
      .success(function() {
        Auth.login();
        $location.path('/profile');
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };
});

app.controller('LogoutController', function ($scope, $http, $location, Auth) {
  $http.get('/api/logout')
    .success(function() {
      Auth.logout();
      $location.path('/');
    })
    .error(function(err, status) {
      $scope.error = {message: err.message, status: status};
    });
});

app.controller('ExecuteController', function ($scope, $http, $location, $routeParams) {
  $scope.loading = true;

  var data = {
    'payment_id' : $routeParams.paymentId,
    'payer_id' : $routeParams.PayerID
  };

  $http.put('/api/tickets/pay/execute', data)
    .success(function(data) {
      $scope.loading = false;
      $scope.message = data.message;
    })
    .error(function(err, status) {
      $scope.loading = false;
      $scope.error = {message: err.message, status: status};
    });
});

app.controller('ProfileController', function ($scope, $http, Auth) {
  $scope.alerts= [];
  $scope.state = {
    submitted: false,
    loading: false,
    success: false,
    error: false,
    usernameChanged: false,
    emailChanged: false,
    usernameAvailable: false,
    emailAvailable: false
  };

  $scope.init = function() {
    if (Auth.isLoggedIn()) {
      $http.get('/api/profile')
        .success(function(data) {
          $scope.userData = data.user;
          $scope.formUser = angular.copy($scope.userData);
          $scope.resetMods();
        })
        .error(function(err, status) {
          $scope.error = {message: err.message, status: status};
        });
      $http.get('/api/users/ticket')
        .success(function(data) {
          if (data.ticket) {
            $scope.userTicket = data.ticket;
            $scope.qrCodeString = data.ticket.qr_url;
          }
        })
        .error(function(err) {
          $scope.alerts.push({msg: err.message, type: 'danger'});
        });
    }
  };

  $scope.init();
  $scope.$on('login', function() {
    $scope.init();
  });

  $scope.submitUserMods = function () {
    $http.put('/api/users', $scope.formUser)
      .success(function(data) {
        $scope.userData = data.user;
        $scope.resetMods();
        $scope.alerts.push({msg: 'Vos informations ont été mises à jour.', type: 'success'});
      })
      .error(function(err) {
        $scope.alerts.push({msg: err.message, type: 'danger'});
      });
  };
  $scope.resetMods = function () {
    $scope.edit = false;
    $scope.formUser = angular.copy($scope.userData);
    $scope.state.emailAvailable = true;
    $scope.state.emailChanged = true;
    $scope.state.usernameAvailable = true;
    $scope.state.usernameChanged = true;
  };
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
      .error(function() {
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
      .error(function() {
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
      $scope.error = {message: err.message, status: status};
    });
});

app.controller('SignupController', function($scope, $http, $modal) {
  $scope.state = {
    submitted: false,
    loading: false,
    success: false,
    error: false,
    usernameChanged: false,
    emailChanged: false,
    usernameAvailable: false,
    emailAvailable: false
  };
  $scope.signup = function(data) {
    $scope.state.loading = true;
    $scope.state.submitted = true;
    $http.post('/api/users', data)
      .success(function(res) {
        $scope.message = res.message;
        $scope.state.loading = false;
        $scope.state.success = true;
      })
      .error(function() {
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
      .error(function() {
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
  $scope.modal = function() {
    var modalInstance = $modal.open({
      controller: 'SignupModalController',
      templateUrl: 'partials/signup-modal.html',
      size: 'lg'
    });
    modalInstance.result.then(function(checked) {
      $scope.checked = checked;
    });
  };
});

app.controller('SignupModalController', function($scope, $modalInstance) {
  $scope.ok = function() {
    $modalInstance.close(true);
  };
  $scope.cancel = function() {
    $modalInstance.close(false);
  };
});

app.controller('MapController', function($scope, $http, $interval, $location, Auth, Timer) {
  $scope.canBuy = false;
  $scope.submitted = false;
  $scope.selectedSeat = null;
  $scope.userPaidSeatID = 0;
  $scope.userTicketSeatID = 0;
  $scope.userTicketOwner = null;
  var seatStatus = {};
  var seatOwners = {};
  var seatUntils = {};

  $scope.resetSelectedSeat = function() {
    $scope.submitted = false;
    $scope.selectedSeat = false;
    delete $scope.selectedSeatID;
    delete $scope.selectSeatIsFree;
    delete $scope.selectedSeatTicketPaid;
    delete $scope.selectedSeatUser;
    delete $scope.selectedSeatUntil;
    delete $scope.selectedSeatIsUserPaidSeat;
  };
  $scope.isAvail = function(seat) {
    return !seatStatus.hasOwnProperty(seat);
  };
  $scope.isSelected = function(seat) {
    return $scope.selectedSeatID == seat
  };
  $scope.isReserved = function(seat) {
    return seatStatus[seat] == 'r';
  };
  $scope.isTaken = function(seat) {
    return seatStatus[seat] == 't';
  };
  $scope.isAlreadyReserved = function(seat) {
    return $scope.userTicketSeatID == seat && $scope.getOwner(seat) == $scope.userTicketOwner;
  };
  $scope.isUser = function(seat) {
    return $scope.userPaidSeatID == seat;
  };
  $scope.getOwner = function(seat) {
    return seatOwners[seat];
  };
  $scope.getUntil = function(seat) {
    return seatUntils[seat];
  };
  $scope.times = function(x) {
    return new Array(x);
  };

  $scope.init = function() {
    if (Auth.isLoggedIn()) {
      $http.get('/api/users/ticket')
        .success(function (data) {
          if (data.ticket && data.ticket.type_id !== TICKET_TYPES.PC && !data.ticket.paid) {
            $location.path('/pay');
          }
          if (data.ticket && data.ticket.paid) {
            $scope.userPaidSeatID = data.ticket.seat_num;
          }
          if (data.ticket && !data.ticket.paid) {
            $scope.selectSeat(data.ticket.seat_num);
            $scope.userTicketSeatID = data.ticket.seat_num;
            $scope.userTicketOwner = data.ticket.owner_username;
          }
          if (data.ticket && !data.ticket.paid && data.ticket.now && data.ticket.reserved_until) {
            Timer.bootstrap($scope, data.ticket.now, data.ticket.reserved_until);
          }
          $scope.canBuy = ($scope.loggedIn && !data.ticket) || ($scope.loggedIn && data.ticket && !data.ticket.paid)
        })
        .error(function (err, status) {
          $scope.error = {message: err.message, status: status};
        });
    }
  };

  $scope.init();
  $scope.$on('login', function() {
    $scope.init();
  });

  $scope.selectSeat = function(seat) {
    $scope.resetSelectedSeat();
    $scope.selectedSeat = true;
    $scope.selectedSeatID = seat;

    if (!$scope.isAvail(seat)) {
      $scope.selectSeatIsFree = false;
      $scope.selectedSeatTicketPaid = $scope.isTaken(seat);
      $scope.selectedSeatUser = $scope.getOwner(seat);
      $scope.selectedSeatUntil =  $scope.getUntil(seat);

      if ($scope.selectedSeatID == $scope.userPaidSeatID) {
        $scope.selectedSeatIsUserPaidSeat = true;
      }
    } else {
      $scope.selectSeatIsFree = true;
    }
  };

  $scope.buy = function(seat) {
    $scope.submitted = true;

    var ticket = {};
    ticket.type = TICKET_TYPES.PC;
    ticket.seat = seat;

    $http.get('/api/users/ticket')
      .success(function(data) {
        if (data.ticket) {
          if (data.ticket.seat_num == seat && $scope.userTicketSeatID == seat) {
            $location.path('/pay');
          } else {
            $http.put('/api/tickets/seat', ticket)
              .success(function() {
                $location.path('/pay');
              })
              .error(function(err, status) {
                $scope.error = {message: err.message, status: status};
              });
          }
        } else {
          $http.post('/api/tickets', ticket)
            .success(function() {
              $location.path('/pay');
            })
            .error(function(err, status) {
              $scope.error = {message: err.message, status: status};
            });
        }
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.refresh = function() {
    $http.get('/api/tickets/type/0')
      .success(function(data) {
        seatStatus = {};
        seatOwners = {};
        seatUntils = {};
        var tickets = data.tickets;
        for (var i = 0; i < tickets.length; i++) {
          var seat = tickets[i].seat_num;
          if (tickets[i].paid) {
            seatStatus[seat] = 't';
          } else {
            seatStatus[seat] = 'r';
          }
          seatOwners[seat] = tickets[i].owner_username;
          seatUntils[seat] = tickets[i].reserved_until;
        }
        if ($scope.selectedSeat) {
          $scope.selectSeat($scope.selectedSeatID);
        }
      })
      .error(function(err, status) {
        $scope.error = {message: err.message, status: status};
      });
  };

  $scope.refresh();
  $scope.intervalPromise = $interval(function() {
    $scope.refresh();
  }, 5000);
  $scope.$on('$destroy', function() {
    $interval.cancel($scope.intervalPromise);
  });
});

app.config(function($routeProvider, $locationProvider, cfpLoadingBarProvider) {
  $routeProvider
  .when('/', {
    templateUrl: 'partials/home.html',
    controller: 'HomeController'
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
