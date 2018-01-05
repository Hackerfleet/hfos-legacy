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
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
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
    constructor($scope, $rootScope, $compile, ObjectProxy, timeout, user, moment, notification, $aside, $modal, socket, $filter) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.compile = $compile;
        this.moment = moment;
        this.op = ObjectProxy;
        this.timeout = timeout;
        this.user = user;
        this.notification = notification;
        this.socket = socket;
        this.filter = $filter;

        this.eventSources = [];
        let now = new Date();

        this.calendar_events = [];
        this.notificationMessage = "";

        this.calendars = {};

        this.calendars_own = [];
        this.calendars_other = [];

        this.enabled = [];

        this.selected_event = null;
        this.new_event = null;

        this.events = [];

        this.active_tab = 0;

        this.default_buttons = 'today month,agendaWeek,twoWeek,agendaDay prev,next hideButton';

        this.business_time = {
            dow: [1, 2, 3, 4, 5],
            start: '08:00',
            end: '18:00'
        };

        this.first_day = 1;

        let self = this;

        this.pushEvent = function (event, uuid) {
            let color = null;
            if (typeof event.color !== 'undefined' && event.color !== "") {
                color = event.color;
            } else {
                color = self.calendars[uuid].color;
            }
            let ev = {
                title: event.name,
                start: event.dtstart,
                end: event.dtend,
                uuid: event.uuid,
                calendar_uuid: uuid,
                color: color,
                allDay: false,
                className: ['calendar-event']
            };
            self.calendar_events.push(ev);
        };

        this.popEvent = function (uuid) {
            console.log('[CALENDAR] Popping event');
            for (let item of self.calendar_events) {
                if (item.uuid === uuid) {
                    console.log('[CALENDAR] Removed element:', item);
                    self.calendar_events.pop(item);
                    break;
                }
            }
        };

        this.popCalendar = function (uuid) {
            console.log('[CALENDAR] Popping calendar', self.calendar_events);
            let dropped = [];
            for (let item of self.calendar_events) {
                console.log('item:', item);
                console.log('itemuuid:', item.calendar_uuid, 'uuid:', uuid);
                if (item.calendar_uuid === uuid) {
                    dropped.push(item);
                    console.log('Popped event:', item);
                }
            }
            for (let item of dropped) {
                self.calendar_events.pop(item);
            }
            console.log("NOW:", self.calendar_events);
        };

        this.getEvents = function (uuid) {
            this.op.searchItems('event', {calendar: uuid}, '*').then(function (msg) {
                console.log('[CALENDAR] Events for calendar ', uuid, ':', msg.data);
                console.log(self.calendars[uuid].color);

                self.popCalendar(uuid);

                for (let event of msg.data) {
                    self.pushEvent(event, uuid);
                }
                console.log('[CALENDAR] Event list for calendar:', self.calendar_events);

            });
        };
        this.rootscope.$on('OP.Put', function (event, schema, uuid, obj) {
            console.log('Op Put calendar', schema, uuid, obj, self.enabled);
            if (schema === 'event' && self.enabled.indexOf(obj.calendar) >= 0) {
                console.log('[CALENDAR] Pushing new published event');
                self.pushEvent(obj, obj.calendar);
            }
        });

        this.rootscope.$on('OP.Deleted', function (event, schema, uuid) {
            if (schema === 'event') {
                console.log('[CALENDAR] Event was deleted', uuid);
                self.popEvent(uuid);
            }
        });

        this.getData = function () {
            this.op.searchItems('calendar', '*', '*').then(function (result) {
                console.log('[CALENDARS] Got the list of calendars:', result);
                for (let item of result.data) {
                    self.calendars[item.uuid] = item;
                    self.calendars[item.uuid].enabled = false;
                    self.enabled.push(item.uuid);


                    // TODO: Remove this and store self.enabled somewhere, so it is persistent
                    // Should be filled with any own calendars on first unset encounter
                    //self.calendars[item.uuid].enabled = self.enabled.indexOf(item.uuid) >= 0;
                    self.toggle_calendar(item.uuid);

                }

                console.log('[CALENDARS] List of calendars:', self.calendars);
                self.filter_calendars();
            });


        };

        this.filter_calendars = function () {
            console.log('[CALENDAR] Filtering own calendars:', self.user.useruuid);
            for (let key of Object.keys(self.calendars)) {
                let cal = self.calendars[key];
                console.log('cal:', cal, key);
                if (cal.owner === self.user.useruuid) {
                    self.calendars_own.push(key);
                } else {
                    self.calendars_other.push(key);
                }
            }
        };


        this.eventSources = [this.calendar_events];

        /*
        this.calendarView = 'month';
        this.calendarDate = new Date();
        this.calendarTitle = 'Shareables for %NAME';
        */


        this.alertOnDayClick = function (date, jsEvent, view) {
            console.log('jsEvent:', jsEvent, view);

            self.notificationMessage = (date.format() + ' was clicked ');
            self.selected_event = null;
            let start = new Date(date);
            let end = new Date(start);
            end.setHours(start.getHours() + 1);
            self.new_event = {
                dtstart: start.toISOString(),
                dtend: end.toISOString()
            };
            console.log('[CALENDAR] Updated model:', self.new_event);
            self.scope.$broadcast('Changed.Initial', self.new_event);
            self.active_tab = 1;
            self.scope.$broadcast('Resize', '<75%');
        };

        /* alert on eventClick */
        this.alertOnEventClick = function (date, jsEvent, view) {
            self.notificationMessage = (date.title + ' was clicked ');
            console.log('CAL-Ev:', date, jsEvent);
            self.selected_event = date.uuid;
            console.log('EMITTING');
            self.scope.$broadcast('Changed.UUID', self.selected_event);
            self.active_tab = 1;
            self.scope.$broadcast('Resize', '<75%');
        };
        /* alert on Drop */
        this.alertOnDrop = function (event, delta, revertFunc, jsEvent, ui, view) {
            self.notificationMessage = ('Event Droped to make dayDelta ' + delta);
        };
        /* alert on Resize */
        this.alertOnResize = function (event, delta, revertFunc, jsEvent, ui, view) {
            self.notificationMessage = ('Event Resized to make dayDelta ' + delta);
        };

        this.toggleButtons = function () {
            console.log('Toggling button bar visibility');
            $('.fc-right').toggle();

        };

        this.scope.$on('User.Login', function (ev) {
            self.getData();
        });

        if (this.user.signedin) {
            self.getData();
        }

        this.eventRender = function (event, element, view) {
            console.log('element:', element);
            element.attr({
                'tooltip': event.title,
                'tooltip-append-to-body': true
            });
            element[0].innerHTML = self.filter('embed')(event.title);
            self.compile(element)(self);
        };

        this.uiConfig = {
            calendar: {
                height: 'parent',
                editable: true,
                weekNumbers: true,
                header: {
                    left: 'title',
                    center: '',
                    right: self.default_buttons
                },
                navLinks: true,
                views: {
                    twoWeek: {
                        type: 'basic',
                        duration: {weeks: 2},
                        rows: 2,
                        buttonText: '2 Weeks'
                    }
                },
                businessHours: this.business_time,
                firstDay: this.first_day,
                eventClick: this.alertOnEventClick,
                eventDrop: this.alertOnDrop,
                eventResize: this.alertOnResize,
                eventRender: this.eventRender,
                dayClick: this.alertOnDayClick,
                weekClick: function () {
                    console.log('WEEK CLICKED');
                },
                viewRender: function (view, element) {
                    console.log("View Changed: ", view.visStart, view.visEnd, view.start, view.end);
                }
            }
        };
    }

    switch_view(view) {
        $('#calendar').fullCalendar('changeView', view);
    }

    goto_date(date) {
        $('#calendar').fullCalendar('gotoDate', date);
    }

    toggle_calendar(uuid) {
        console.log('[CALENDAR] Toggling calendar:', uuid);
        if (this.calendars[uuid].enabled) {
            this.calendars[uuid].enabled = false;
            this.enabled.pop(uuid);
            this.popCalendar(uuid);
        } else {
            this.calendars[uuid].enabled = true;
            this.enabled.push(uuid);
            this.getEvents(uuid);
        }
        console.log('[CALENDAR] Result: ', this.calendars, this.enabled);

    }
}

CalendarCtrl.$inject = ['$scope', '$rootScope', '$compile', 'objectproxy', '$timeout', 'user', 'moment', 'notification', '$aside', '$modal', 'socket', '$filter'];

export default CalendarCtrl;
