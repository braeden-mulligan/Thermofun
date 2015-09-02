var panel = angular.module('panel', []);

panel.controller('mainController', function($scope) {
    $scope.enabled = true;
    $scope.temperature = '27';
});
