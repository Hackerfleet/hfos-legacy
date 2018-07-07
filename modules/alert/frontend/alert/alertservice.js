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
 * @ngdoc service
 * @name hfosFrontendApp.alertservice
 * @description
 * # alertservice
 * Service in the hfosFrontendApp.
 */

class alertservice {
    
    constructor(user, notification, interval, timeout, socket, rootscope, navbar) {
        this.user = user;
        this.notification = notification;
        this.interval = interval;
        this.timeout = timeout;
        this.socket = socket;
        this.rootscope = rootscope;

        navbar.add('alertbutton');

        this.blink_state = 0;
        this.blinker = null;
        this.triggered = false;
        this.alert = null;
        this.action = null;


        let self = this;

        this.blink_stop = function() {
            $('#btnalert').css('color', '');
            self.blink_state = 0;
            self.interval.cancel(self.blinker);
            self.blinker = null;
        };

        this.blink_func = function () {
            let state = self.blink_state;
            console.log('Blinkstate:', state);
            
            if  (state === 1) {
                $('#btnalert').css('color', '#f00');
                self.blink_state++;
            } else if (state === 2) {
                $('#btnalert').css('color', '#ff0');
                self.blink_state = 1;
            }
        };

        this.toggle_alert = function() {
            console.log('[ALERT] Triggering', self.triggered);
            let delay;


            if (self.triggered === false) {
                console.log('[ALERT] ALERTING');
                this.action = 'trigger';
                delay = 1000;
            } else {
                this.action = 'cancel';
                delay = 5000;
            }
            let msg = {
                component: 'hfos.alert.manager',
                action: this.action,
                data: {
                    topic: 'mob',
                    msg: 'Man Over Board Alert!'
                }
            };
            this.alert = this.timeout(this.send_alert, delay, false, msg);
        };

        this.send_alert = function(msg) {
            self.socket.send(msg);
            self.action = null;
        };

        this.untrigger = function() {
            console.log('[ALERT] Cancelling trigger');
            if (this.action !== null) {
                this.notification.add('warning', 'Hold pressed', 'Keep this button pressed longer to trigger an alert change.', 5);
            }
            this.timeout(self.timeout.cancel, 100, false, self.alert);
        };

        this.socket.listen('hfos.alert.manager', function(msg) {
            if (msg.action === 'trigger') {
                self.triggered = true;
                self.notification.add('danger', msg.data.title, msg.data.message, 30);
                if (self.blinker === null) {
                    self.blink_state = 1;
                    self.blinker = self.interval(self.blink_func, 1000)
                }
            } else if (msg.action === 'cancel') {
                self.triggered = false;
                self.blink_stop();
            }
        });

        console.log('[ALERT] ALERT LOADED');
    }
}

alertservice.$inject = ['user', 'notification', '$interval', '$timeout', 'socket', '$rootScope', 'navbar'];

export default alertservice;
