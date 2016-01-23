'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:LibraryCtrl
 * @description
 * # LibraryCtrl
 * Controller of the hfosFrontendApp
 */
angular.module('hfosFrontendApp')
    .controller('LibraryCtrl', function ($scope, $route, $location, ObjectProxy) {
        $scope.searchISBN = '';
        $scope.searchMeta = '';

        $scope.searching = false;

        $scope.searchByISBN = function () {
            $scope.searching = true;

            console.log('Searching for book by ISBN:', $scope.searchISBN);
            ObjectProxy.getlist('book', {'isbn': $scope.searchISBN}, ['*']);
        };

        $scope.$on('OP.ListUpdate', function (ev, update) {
            console.log('OH, HELLO!', ev, update);
            $location.path('list/book');
            //$route.reload();

        });

        $scope.searchByMeta = function () {
            console.log('Searching for book by Metadata:', $scope.searchMeta);

        };
    })
    .config(function ($routeProvider) {
        $routeProvider
            .when('/library', {
                templateUrl: 'views/library.html'
            });
    });
