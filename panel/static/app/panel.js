var panel = angular.module('panel', ['rzModule']);

panel.controller('mainController', function($scope) {
    $scope.enabled = true;
    $scope.temperature = '27';
});
