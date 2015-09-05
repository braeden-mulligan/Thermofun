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
      }, function (error) {
        $scope.reportErrorToUser(error);
      });
  };

  $scope.increaseTemp = function () {
    $scope.enabled = true;
    $scope.targetTemp = $scope.targetTemp + 1;
    $scope.writeSettings();
  };

  $scope.decreaseTemp = function () {
    $scope.enabled = true;
    $scope.targetTemp = $scope.targetTemp - 1;
    $scope.writeSettings();
  };

  $scope.toggleEnabled = function () {
    $scope.enabled = !$scope.enabled;
    $scope.writeSettings();
  };

  //TODO: 'Debounce' writes
  //TODO: Ensure backend data stays sync'd to frontend data (right now we just
  //      update the FE values and assume the BE was successfully updated as well)
  $scope.writeSettings = function () {
    $http.post('/api/settings/', {
      "target_temp": $scope.targetTemp,
      "enabled": $scope.enabled
    }).
      then(function (response) {
        console.log("Settings updated!");
      }, function (error) {
        $scope.reportErrorToUser(error);
      })
  };

  $scope.reportErrorToUser = function (error) {
    $scope.errorMsg = JSON.stringify(error, null, 2);
    $scope.wasError = true;
  };

  $scope.init();
});
