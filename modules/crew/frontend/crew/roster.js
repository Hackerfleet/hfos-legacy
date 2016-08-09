'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:CrewCtrl
 * @description
 * # CrewCtrl
 * Controller of the hfosFrontendApp
 */
class Crew {

    constructor(scope, $modal, navdata, user, objectproxy, socket, menu) {
        this.scope = scope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
    }
}

Crew.$inject = ['$scope', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu'];

export default Crew;