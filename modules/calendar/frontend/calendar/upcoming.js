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
 * @name hfosFrontendApp.controller:CalendarCtrl
 * @description
 * # CalendarCtrl
 * Controller of the hfosFrontendApp
 */

class CalendarCtrl {
    constructor($scope, $rootScope, $compile, ObjectProxy, timeout, user, moment, socket, $filter) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.compile = $compile;
        this.moment = moment;
        this.op = ObjectProxy;
        this.timeout = timeout;
        this.user = user;
        this.socket = socket;
        this.filter = $filter;


        let now = new Date();

        this.limit = 5;
        this.events = [];
        this.calendars = ['bfdfec2a-81e2-4838-b2a6-f11ad0128211'];
        this.calendars_available = [];

        let self = this;

        this.getCalendars = function () {
            this.op.search('calendar', '*').then(function (msg) {
                console.log('[UPCOMING] Calendars:', msg);
                let calendars = msg.data.list;
                self.calendars_available = calendars;
            });
        };

        this.rootscope.$on('OP.Deleted', function (event, schema, uuid) {
            if (schema === 'event') {
                console.log('[UPCOMING] Event was deleted', uuid);
                self.popEvent(uuid);
            }
        });

        this.getEvents = function () {
            for (let uuid of self.calendars) {
                self.op.search('event', {calendar: uuid, dtstart: {'$gt': now}}, '*', '', true, self.limit).then(function (msg) {
                    console.log('[UPCOMING] Events:', msg);
                    let events = msg.data.list;
                    for (let item of events) {
                        self.events.push(item);
                    }
                });
            }
            console.log('[UPCOMING] Events after update:', self.events);
        };

        this.getData = function() {
            this.getCalendars();
            this.getEvents();
        };

        this.scope.$on('User.Login', function (ev) {
            self.getData();
        });

        if (this.user.signedin) {
            self.getData();
        }

    }

}

CalendarCtrl.$inject = ['$scope', '$rootScope', '$compile', 'objectproxy', '$timeout', 'user', 'moment', 'socket', '$filter'];

export default CalendarCtrl;
