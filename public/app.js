var app = angular.module('App', ['ngRoute']);

app.controller('UsersController', function($scope, $http) {
  $http.get('/api/users')
    .success(function(data, status) {
      $scope.data = data;
    })
    .error(function(err, status) {
      //TODO Provide visual error in view
      console.log(status);
      console.log(err);
    })
});

app.controller('SubscriptionController', function($scope, $http) {
  $scope.subscribe = function(data) {
    $http.post('/api/subscribe', data)
      .success(function(data, status) {
        console.log(status);
      })
      .error(function(data, status) {
        console.log(data);
      });
  }
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
  });
});
