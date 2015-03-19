"use strict";
var app = angular.module('App', ['ngRoute', 'ui.bootstrap']);

app.controller('GamesController', function ($scope, $http) {
  $http.get('/api/games')
    .success(function (data) {
      $scope.data = data;
    })
    .error(function (err, status) {
      $scope.error = {message: err, status: status};
    });
  $scope.isCollapsed = new Array;
  for(var o in $scope.data) {
    $scope.isCollapsed.push(false);
}
  console.log($scope.data);
});

app.controller('UsersController', function ($scope, $http) {
  $http.get('/api/users')
    .success(function (data) {
      $scope.data = data;
    })
    .error(function (err, status) {
      $scope.error = {message: err, status: status};
    });
  $http.get('/api/users/max/pc')
    .success(function (max) {
      $scope.maxPc = max;
    })
    .error(function (err, status) {
      $scope.error = {message: err, status: status};
    });
});

app.controller('SubscriptionController', function ($scope, $http) {
  $scope.subscribe = function (data) {
    $scope.submitted = 0;
    $http.post('/api/subscribe', data)
      .success(function (data, status) {
        console.log(status);
        console.log(data);
        $scope.data = data;
        $scope.submitted = 1;
      })
      .error(function (data) {
        console.log(data);
        $scope.data = data;
        $scope.submitted = -1;
      });
  };
});

app.config(function ($routeProvider, $locationProvider) {
  $routeProvider.when('/', {
    templateUrl: 'partials/home.html'
  })
  .when('/rules', {
    templateUrl: 'partials/rules.html',
  })
  .when('/users', {
    templateUrl: 'partials/users.html',
    controller: 'UsersController'
  })
  .when('/subscribe', {
    templateUrl: 'partials/subscription.html',
    controller: 'SubscriptionController'
  }).when('/games', {
      templateUrl: 'partials/games.html',
      controller: 'GamesController'
  }).when('/congratulations', {
    templateUrl: 'partials/congratulations.html'
  });

  $locationProvider.html5Mode(true);
});
