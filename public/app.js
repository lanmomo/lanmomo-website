"use strict";
var app = angular.module('App', ['ngRoute', 'ui.bootstrap']);

app.controller('NavbarController', function($scope, $location) {
  $scope.isActive = function(url) {
    return $location.path() === url;
  };
});

app.controller('GamesController', function($scope, $http) {
  $http.get('/api/games')
    .success(function(data) {
      $scope.data = data;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
  $scope.isCollapsed = new Array;
  for(var o in $scope.data) {
    $scope.isCollapsed.push(false);
}
  console.log($scope.data);
});

app.controller('UsersController', function($scope, $http) {
  $scope.pcUsers = [];
  $scope.consoleUsers = [];
  $http.get('/api/users')
    .success(function(data) {
      $scope.data = data;
      $scope.data.forEach(function(user) {
        if (user.type == "pc") {
          $scope.pcUsers.push(user);
        } else if (user.type == "console"){
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
    error: false
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
