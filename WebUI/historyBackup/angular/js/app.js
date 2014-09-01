'use strict';

/* App Module */

var historyApp = angular.module('historyApp', [
  'ngRoute',
  'historyAppController',
  'ui.bootstrap', 
  '$strap.directives'
]);
 
historyApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/history', {
        templateUrl: 'angular/partials/event-list.html',
        controller: 'EpisodesListCtrl'
      }).
      when('/history/:eventId', {
        templateUrl: 'angular/partials/event-detail.html',
        controller: 'HistoryDetailCtrl'
      }).
      otherwise({
        redirectTo: '/history'
      });
  }]);
