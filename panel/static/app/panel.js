'use strict';

var panel = angular.module('panel', []);

panel.controller('mainController', function($scope, $http) {

  $scope.init = function () {
    $scope.enabled = false;
    $scope.targetTemp = 0;

    $http.get('/api/settings/').
      then(function (response) {
        $scope.enabled = response.data.enabled ? (response.data.enabled.toLowerCase() == "true") : false;
        $scope.targetTemp = parseInt(response.data.target_temp);
        console.log(response);
      }, function (error) {
        $scope.errorMsg = JSON.stringify(error, null, 2);
        $scope.wasError = true;
      });
  };

  $scope.increaseTemp = function () {
    $scope.enabled = true;
    $scope.targetTemp = $scope.targetTemp + 1;
  };

  $scope.decreaseTemp = function () {
    $scope.enabled = true;
    $scope.targetTemp = $scope.targetTemp - 1;
  };

  $scope.toggleEnabled = function () {
    $scope.enabled = !$scope.enabled;
  };

  $scope.init();
});
