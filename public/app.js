"use strict";
var app = angular.module('App', ['ngRoute', 'ui.bootstrap']);

app.controller('NavbarController', function($scope, $location) {
  $scope.isActive = function(url) {
    return $location.path() === url;
  };
  $('.navbar-nav li a').click(function() {
    if ($('.navbar-collapse.collapse').hasClass('in')) {
      $('#navbar').collapse('hide');
    }
  });
});

app.controller('GamesController', function($scope, $http) {
  $http.get('/api/games')
    .success(function(data) {
      $scope.data = data;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
});

app.controller('UsersController', function($scope, $http) {
  $scope.pcUsers = [];
  $scope.consoleUsers = [];
  $http.get('/api/users')
    .success(function(data) {
      $scope.data = data;
      $scope.data.forEach(function(user) {
        if (user.type === "pc") {
          $scope.pcUsers.push(user);
        } else if (user.type === "console"){
          $scope.consoleUsers.push(user);
        }
      });
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
  $http.get('/api/users/max/pc')
    .success(function(max) {
      $scope.maxPc = max;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
  $http.get('/api/users/max/console')
    .success(function(max) {
      $scope.maxConsole = max;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
});

app.controller('SubscriptionController', function($scope, $http) {
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
  $scope.subscribe = function(data) {
    $scope.state.loading = true;
    $scope.state.submitted = true;
    $http.post('/api/subscribe', data)
      .success(function(data, status) {
        console.log(status);
        console.log(data);
        $scope.data = data;
        $scope.state.loading = false;
        $scope.state.success = true;
      })
      .error(function(data) {
        console.log(data);
        $scope.data = data;
        $scope.state.loading = false;
        $scope.state.error = true;
      });
  };
  $scope.isUsernameAvailable = function(user) {
    $http.post('/api/users/has/username', {username: user.username})
      .success(function(data, status) {
        $scope.state.usernameAvailable = !data.exists;
        $scope.state.usernameChanged = true;
      })
      .error(function(data) {
        console.log(data);
        $scope.state.usernameAvailable = false;
        $scope.state.usernameChanged = true;
      });
  };
  $scope.resetUsernameChanged = function() {
    $scope.state.usernameChanged = false;
  };
  $scope.isEmailAvailable = function(user) {
    $http.post('/api/users/has/email', {email: user.email})
      .success(function(data, status) {
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

app.config(function($routeProvider, $locationProvider) {
  $routeProvider.when('/', {
    templateUrl: 'partials/home.html'
  })
  .when('/users', {
    templateUrl: 'partials/users.html',
    controller: 'UsersController'
  })
  .when('/games', {
    templateUrl: 'partials/games.html',
    controller: 'GamesController'
  })
  .when('/about', {
    templateUrl: 'partials/about.html'
  })
  .when('/rules', {
    templateUrl: 'partials/rules.html'
  })
  .when('/contact', {
    templateUrl: 'partials/contact.html'
  })
  .when('/subscribe', {
    templateUrl: 'partials/subscription.html',
    controller: 'SubscriptionController'
  })
  .when('/congratulations', {
    templateUrl: 'partials/congratulations.html'
  });

  $locationProvider.html5Mode(true);
});
