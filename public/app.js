"use strict";
var app = angular.module('App', ['ngRoute']);

app.controller('UsersController', function($scope, $http) {
  $http.get('/api/users')
    .success(function(data) {
      $scope.data = data;
    })
    .error(function(err, status) {
      $scope.error = {message: err, status: status};
    });
});

app.controller('SubscriptionController', function($scope, $http) {
  $scope.subscribe = function(data) {
    $http.post('/api/subscribe', data)
      .success(function(data, status) {
        //TODO Do something with if 400 or 500
        console.log(status);
        console.log(data);
      })
      .error(function(data) {
        console.log(data);
      });
  };
});


app.config(function($routeProvider) {
  $routeProvider.when('/', {
    templateUrl: 'partials/home.html'
  })
  .when('/users', {
    templateUrl: 'partials/users.html',
    controller: 'UsersController'
  })
  .when('/subscribe', {
    templateUrl: 'partials/subscription.html',
    controller: 'SubscriptionController'
  })
  .when('/congratulations', {
    templateUrl: 'partials/congratulations.html'
  });
});
