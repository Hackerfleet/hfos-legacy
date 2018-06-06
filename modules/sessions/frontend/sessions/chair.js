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

class Sessions {

    constructor(scope, rootscope, user, socket, notification, schemata, objectproxy, filemanagerservice, state, moment) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.user = user;
        this.socket = socket;
        this.notification = notification;
        this.schemata = schemata;
        this.op = objectproxy;
        this.filemanagerservice = filemanagerservice;
        this.state = state;
        this.moment = moment;

        this.form = null;
        this.schema = null;
        this.model = null;
        this.editing = false;

        this.time = new Date;
        this.calendar = "";

        this.calendars = {};

        this.sessions = {};
        this.sessiontypes = {};

        this.reviews = {};
        this.reviews_by_session = {};

        this.dragdata = {
            hello: 'world'
        };

        let self = this;


        this.get_sessiontypes = function () {
            console.log('[SESSIONS] Login successful - fetching session data');

            self.op.search('sessiontype', '*', '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.sessiontypes = {};
                    for (let sessiontype of msg.data.list) {
                        self.sessiontypes[sessiontype.uuid] = sessiontype;
                    }
                } else {
                    self.sessiontypes = {};
                }
            });
        };

        this.get_sessions = function () {
            console.log('[SESSIONS] Login successful - fetching session data');

            self.op.search('session', '*', '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.sessions = {};
                    for (let session of msg.data.list) {
                        // TODO: Get this from another chair-only-writable object
                        self.sessions[session.uuid] = session;
                    }
                } else {
                    self.sessions = {};
                }
            });

            self.op.search('reviews', '*', '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.reviews = {};
                    self.reviews_by_session = {};

                    for (let review of msg.data.list) {
                        self.reviews[review.uuid] = review;
                        self.reviews_by_session[review.session_reference] = review;
                    }
                }
            });

            self.op.search('calendar', '*', '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.calendars = {};

                    for (let calendar of msg.data.list) {
                        self.calendars[calendar.uuid] = calendar;
                    }
                }
            });
        };

        this.get_events = function (only_new) {
            let filter = {
                category: 'session'
            };
            if (only_new === true) {
                filter.dtstart = 'None';
                filter.dtend = 'None';
            }

            self.op.search('event', filter, '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.events = {};

                    for (let event of msg.data.list) {
                        self.events[event.uuid] = event;
                    }
                }
            });
        };

        this.get_user_data = function () {
            console.log('[SESSIONS] Getting user data');

            self.model = {};

            self.get_sessions();
            self.get_sessiontypes();

            self.get_events();

            if (schemata.schemata !== null) {
                self.get_schema();
            }

        };

        this.get_schema = function () {
            console.log('[SESSIONS] Requesting schema');
            self.schema = self.schemata.schema('session');
            self.form = self.schemata.form('session');
        };


        this.getFormData = function (options, search) {
            console.log('[OE] Trying to obtain proxy list.', options, search);
            if (search === '') {
                console.log("INSIDEMODEL:", options.scope.insidemodel);
            }

            let result = self.op.search(options.type, search).then(function (msg) {
                console.log('OE-Data', msg);
                return msg.data.list;

            });
            console.log('[OE] Result: ', result);
            return result;

        };


        if (user.signedin === true) {
            this.get_user_data();
        }

        let schemaHandler = this.rootscope.$on('Schemata.Update', function () {
            console.log('[SESSIONS] Getting schema');
            self.get_schema();
        });

        let loginHandler = this.rootscope.$on('User.Login', function () {
            console.log('[SESSIONS] Logged in, getting user data');
            self.get_user_data();
        });

        let managerHandler = this.socket.listen('hfos.session.sessionmanager', function (msg) {
            console.log('[SESSIONS] Msg', msg);
            if (msg.action === 'session_confirm') {
                self.get_events(true);
            }
        });

        this.scope.$on('$destroy', function () {
            console.log('[SESSIONS] Destroying');
            loginHandler();
            schemaHandler();
            managerHandler();
        });
    }

    is_scheduled(event) {
        console.log('SCHEDULED:', event.dtstart);
        return typeof event.dtstart !== 'undefined'
    }

    set_drag_data(ev, dragEv, data) {
        console.log('[CHAIR] Setting Dragdata to:', data);
        data.dtstart = new Date();
        data.dtend = new Date(new Date().getTime() + (data.duration*60000));
        this.dragdata = data;
    }

    submitSession(no_show) {
        let model = this.model;
        let self = this;
        if (this.editing !== true) {
            model.uuid = 'create';
        }

        console.log('[SESSIONS] Object update initiated with ', model);
        this.op.put('session', model).then(function (msg) {
            if (msg.action !== 'fail') {
                self.model = msg.data.object;
                self.editing = true;

                if (!no_show) self.notification.add('success', 'Submission stored', 'Your session has been submitted successfully.', 5);

                self.get_sessions();
            } else {
                self.notification.add('warning', 'Submission not stored', 'Your session has not been submitted: ' + result.reason, 10);
            }
        });
    }

    deleteSession(uuid) {
        let self = this;

        console.log('[SESSIONS] Requesting session deletion: ', uuid);
        this.op.deleteObject('session', uuid).then(function (msg) {
            if (msg.action !== 'fail') {
                self.notification.add('success', 'Submission deleted', 'Your session has been deleted successfully.', 5);
                delete self.sessions[uuid];
            } else {
                self.notification.add('warning', 'Submission not deleted', 'Your session has not been deleted: ' + result.reason, 10);
            }
        });
    }

    editSession(uuid) {
        console.log('[SESSIONS] Editing session:', uuid);
        this.model = this.sessions[uuid];
        this.editing = true;
    }

    handleReview(uuid, action) {
        console.log('[SESSIONS] Performing ', action, ' on review:', uuid);
        let initial = null;
        let uuid_arg = null;

        if (action === 'confirm') {
            if (this.calendar === '') {
                this.notification.add('warning', 'Select calendar', 'Please select a calendar to confirm this session', 5);
                return
            }
            let request = {
                component: 'hfos.sessions.sessionmanager',
                action: 'session_confirm',
                data: {
                    time: this.time,
                    calendar: this.calendar,
                    session: uuid
                }
            };
            this.socket.send(request);
            return
        } else if (action === 'create') {
            initial = {session_reference: uuid};
        } else {
            uuid_arg = uuid;
        }
        this.state.go('app.editor', {schema: 'review', uuid: uuid_arg, action: action, initial: initial})
    }


    hasReview(uuid) {
        return uuid in this.reviews_by_session;
    }

    can_review() {
        return this.user.account.roles.indexOf('reviewer') >= 0;
    }

    can_confirm() {
        return this.user.account.roles.indexOf('chair') >= 0;
    }
}

Sessions.$inject = ['$scope', '$rootScope', 'user', 'socket', 'notification', 'schemata', 'objectproxy', 'filemanagerservice', '$state', 'moment'];

export default Sessions;
