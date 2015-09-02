'use strict';

var panel = angular.module('panel', []);

panel.controller('mainController', function($scope) {

  $scope.enabled = true;
  $scope.targetTemp = 27;

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
});
