/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2018 riot <riot@c-base.org> and others.
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

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:UpcomingCtrl
 * @description
 * # UpcomingCtrl
 * Controller of the hfosFrontendApp
 */

class UpcomingCtrl {
    constructor($scope, $rootScope, $compile, ObjectProxy, timeout, interval, user, moment, socket, $filter, state, $stateParams) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.compile = $compile;
        this.moment = moment;
        this.op = ObjectProxy;
        this.timeout = timeout;
        this.interval = interval;
        this.user = user;
        this.socket = socket;
        this.filter = $filter;
        this.state = state;
        $scope.stateParams = $stateParams;


        this.now = new Date();
        this.today = new Date().setHours(0, 0, 0, 0);

        this.limit = 5;
        this.events = [];
        this.calendars = {};
        this.calendars_available = [];
        this.calendars_enabled = [];
        this.multi_calendar = false;
        this.show_only_upcoming = false;

        let self = this;

        this.clock_update = this.interval(function () {
            self.now = new Date();
            self.five_minutes = new Date(self.now.getTime() + (5 * 60000));
            self.today = new Date().setHours(0, 0, 0, 0);
            self.events.forEach(function (event) {
                event._eta = moment(event.dtstart).fromNow();
            });
        }, 500);

        this.getEvents = function () {
            console.log('[UPCOMING] Getting events');

            this.op.search('calendar', '*').then(function (msg) {
                console.log('[UPCOMING] Calendars:', msg);
                self.calendars = {};
                self.calendars_available = [];
                self.events = [];

                for (let calendar of msg.data.list) {
                    self.calendars[calendar.uuid] = calendar;
                    self.calendars_available.push({
                        value: calendar.uuid,
                        label: calendar.name
                    });
                }

                self.multi_calendar = self.calendars_available.length > 1;

                // TODO: Get this from state parameters
                if (self.calendars_enabled.length === 0) {
                    self.calendars_enabled.push(self.calendars[0].uuid);
                }

                console.log('Transitioning:');
                self.state.transitionTo('app.upcoming', {calendars: JSON.stringify(self.calendars_enabled)}, {
                    location: 'replace',
                    notify: false
                });

                console.log('[UPCOMING] Fetching events for all enabled calendars');
                let filter = {
                    calendar: {'$in': self.calendars_enabled},
                    dtstart: {'$gt': self.now}
                };

                self.op.search('event', filter, '*', '', true, self.limit, 0, [['dtstart', 'asc']]).then(function (msg) {
                    console.log('[UPCOMING] Events:', msg);
                    let events = msg.data.list;
                    for (let item of events) {
                        item._day = new Date(item.dtstart).setHours(0, 0, 0, 0);
                        item.dtstart = new Date(item.dtstart);
                        self.events.push(item);
                    }

                    self.events.sort(function (a, b) {
                        return a.dtstart - b.dtstart;
                    });
                    console.log('[UPCOMING] Events after update:', self.events);
                });


            });


        };

        this.getData = function () {
            this.getEvents();
        };

        this.login_update = this.scope.$on('User.Login', function (ev) {
            self.getData();
        });

        if (this.user.signedin) {
            self.getData();
        }

        this.delete_update = this.rootscope.$on('OP.Deleted', function (event, schema, uuid) {
            if (schema === 'event') {
                console.log('[UPCOMING] Event was deleted', uuid);
                self.popEvent(uuid);
            }
        });

        this.scope.$on('$destroy', function () {
            self.login_update();
            self.delete_update();
        });

    }

    $onInit() {
        console.log('[UPCOMING] State parameters', this.scope.stateParams, this.scope, this.scope.stateParams.calendars);
        this.calendars_enabled = JSON.parse(this.scope.stateParams.calendars);
    }

}

UpcomingCtrl.$inject = [
    '$scope', '$rootScope', '$compile', 'objectproxy', '$timeout', '$interval',
    'user', 'moment', 'socket', '$filter', '$state', '$stateParams'
];

export default UpcomingCtrl;
