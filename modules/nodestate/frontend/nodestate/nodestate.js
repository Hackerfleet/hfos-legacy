/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2017 riot <riot@c-base.org> and others.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

'use strict';

let humanizeDuration = require('humanize-duration');

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:NodestateCtrl
 * @description
 * # NodestateCtrl
 * Controller of the hfosFrontendApp
 */
class Nodestate {

    constructor($scope, $rootscope, $modal, navdata, user, objectproxy, socket, menu, $timeout) {
        this.scope = $scope;
        this.rootscope = $rootscope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
        this.timeout = $timeout;


        this.humanize = humanizeDuration;

        this.now = new Date() / 1000;
        this.lockState = false;
        this.showBoxes = true;

        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 50,
            rowHeight: 75,
            colWidth: 50,
            floating: false,
            draggable: {
                enabled: false
            },
            resizable: {
                enabled: false
            }
        };

        this.gridChangeWatcher = null;

        this.changetimeout = null;

        this.nodestates = {};

        let self = this;

        this.stopSubscriptions = function () {
            console.log('[STATE] Finally destroying all subscriptions');
            self.stopObserved();
            //self.socket.unlisten('hfos.navdata.sensors', self.handleNavdata);
        };

        this.statechange = self.rootscope.$on('$stateChangeStart',
            function (event, toState, toParams, fromState, fromParams, options) {
                console.log('STATE] States: ', toState, fromState);
                if (toState != 'Nodestate') {
                    self.stopSubscriptions();
                }
            });

        this.loginupdate = this.rootscope.$on('User.Login', function () {
            console.log('[STATE] Login successful - fetching nodestate data');
            self.requestNodestates();
        });


        self.scope.$on('$destroy', function() {
            self.stopSubscriptions();
            self.clientconfigupdate();
            self.loginupdate();
            self.statechange();
        });

        this.scope.$on('OP.Update', function (event, uuid, data, schema) {
            if (schema === 'nodestate') {
                console.log('[STATE] Nodestate update received:', uuid, schema, data);
                self.nodestates[uuid] = data;
            }
        });

        this.handleGridChange = function (newVal, oldVal) {
            if (newVal === oldVal) {
                console.log('No actual change');
                return;
            }
            if (self.changetimeout !== null) {
                self.timeout.cancel(self.changetimeout);
            }
            self.changetimeout = self.timeout(self.storeMenuConfig, 5000);
        };

        this.storeMenuConfig = function () {
            console.log('[STATE] Pushing nodestate');

            for (let state of Object.values(self.nodestates)) {
                delete state['$$hashKey'];
                self.op.putObject('nodestate', state);
            }

            self.changetimeout = null;
        };

        this.requestNodestates = function () {
            console.log('[STATE] Getting list of nodestates');
            self.op.search('nodestate', '*', '*', null, true).then(function(msg) {
                console.log('[STATE] States list incoming msg:', msg);

                for (let item of msg.data) {
                    console.log('[STATE] Analysing ', item);
                    self.nodestates[item.uuid] = item;
                }
            });
        };

        if (this.user.signedin === true) {
            console.log('[STATE] Logged in - fetching nodestate data');
            this.requestNodestates();
        }

        this.stopObserved = function() {
            self.op.unsubscribe(Object.keys(self.nodestates));
        };

        console.log('[STATE] Starting');
    }
    toggle(uuid) {
        console.log('[STATE] Toggling ', uuid);
        let state = this.nodestates[uuid];
        if (!state.disabled) {
            console.log('[STATE] Toggling:', state.active);
            let request = {
                component: 'hfos.nodestate.manager',
                action: 'toggle',
                data: uuid
            };
            this.socket.send(request);
        } else {
            console.log('[STATE] Button disabled');
        }
    }

    toggleLock() {
        this.lockState = !this.lockState;
        this.gridsterOptions.draggable.enabled = this.lockState;
        this.gridsterOptions.resizable.enabled = this.lockState;
        if (this.lockState) {
            console.log('Enabling gridwatcher');
            this.gridChangeWatcher = this.scope.$watch('$ctrl.nodestates', this.handleGridChange, true);
        } else {
            this.gridChangeWatcher();
        }
    }
}

Nodestate.$inject = ['$scope', '$rootScope', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu', '$timeout'];

export default Nodestate;
