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
 * @name hfosFrontendApp.controller:EnrolCtrl
 * @description
 * # EnrolCtrl
 * Controller of the hfosFrontendApp
 */
class Enrol {

    constructor($location, scope, rootscope, notification, user, objectproxy, socket) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.notification = notification;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;

        this.enrollments = {};

        this.invitations = [{
            name: '',
            email: ''
        }];

        // TODO: Fix the url. Needs to be constructed from the public/internal hostname, should be switchable in ui
        this.invite_url = $location.protocol() + '://' + $location.host() + ":" + $location.port() + '/#!/invitation/';

        this.checked_enrollments = {};
        this.all_enrollments = false;
        this.action_enrollments = '';

        this.badge = false;

        let self = this;

        this.socket.listen('hfos.enrol.manager', function (msg) {
            console.log('[ENROL] Message received');
            if (msg.action === 'invite') {
                let result = msg.data[true];
                if (typeof result !== 'undefined') {
                    self.enrollments[result.uuid] = result;
                    for (let invitation of self.invitations) {
                        if (invitation.name === result.name) {
                            self.invitations.pop(invitation);
                        }
                    }
                    console.log('Length:', self.invitations.length);
                    if (self.invitations.length === 0) {
                        // Repopulate with a blank form element
                        self.invitations = [{
                            name: '',
                            email: ''
                        }];
                    }
                    self.notification.add('success', 'Enrol', 'Invitations sent to ' + result.email, 3);
                    self.update_badge();
                }
            } else if (msg.action === 'change') {
                let result = msg.data[true];
                if (typeof result === 'undefined') {
                    self.notification.add('warning', 'Enrol', 'Enrollment change failed', 3);
                } else if (result === 'Resent') {
                    self.notification.add('info', 'Enrol', 'Resent invitation mail', 3);
                } else {
                    console.log('[ENROL] Changed:', result);
                    self.enrollments[result.uuid] = result;
                }
                self.update_badge();
            } else {
                console.log('[ENROL] Unkown action:', msg.action, msg.data);
            }
        });

        this.get_data = function () {
            console.log('[ENROL] Getting data');
            this.op.search('enrollment', '*', '*').then(function (msg) {
                let enrollments = msg.data.list;
                console.log('[ENROL] Data received:', enrollments);

                for (let enrollment of enrollments) {
                    self.enrollments[enrollment.uuid] = enrollment;
                }
                self.update_badge();
            })
        };

        if (this.user.signedin) {
            console.log('[ENROL] Already logged in - getting data');
            this.get_data();
        }

        this.rootscope.$on('User.Login', function () {
            console.log('[ENROL] Login - getting data');
            self.get_data();
        });

        this.rootscope.$on('OP.Deleted', function (event, schema, uuid) {
            console.log('Deletion!', schema, uuid);
            if (schema === 'enrollment') {
                console.log('[ENROL] Enrollment deleted:', uuid);
                delete(self.enrollments[uuid]);
                delete(self.checked_enrollments[uuid]);
                self.update_badge();
            }
        })
    }

    get_qr(uuid) {
        return this.invite_url + '/' + uuid;
    }

    toggle_enrollments() {
        for (let enrollment of Object.keys(this.enrollments)) {
            this.checked_enrollments[enrollment] = this.all_enrollments;
        }
    }

    act_enrollments() {
        for (let uuid of Object.keys(this.checked_enrollments)) {
            if (this.checked_enrollments[uuid] === true) {
                this.set_status(uuid, this.action_enrollments);
            }
        }
        if (this.action_enrollments === 'Deleted') {
            this.all_enrollments = false;
        }
        this.action_enrollments = null;
    }

    set_status(uuid, status) {
        console.log('[ENROL] Changing enrollment status', uuid, 'to', status);
        if (status === 'Deleted') {
            this.op.deleteObject('enrollment', uuid);
        } else {
            let request = {
                component: 'hfos.enrol.manager',
                action: 'change',
                data: {
                    uuid: uuid,
                    status: status
                }
            };
            this.socket.send(request);
        }
    }

    invite(method) {
        for (let item of this.invitations) {
            console.log('[ENROL] Inviting user:', item);
            let request = {
                component: 'hfos.enrol.manager',
                action: 'invite',
                data: {
                    name: item.name,
                    email: item.email,
                    method: method
                }
            };
            this.socket.send(request);
        }
    }

    add_invitation_row() {
        this.invitations.push({name: '', email: ''});
    }

    remove_invitation_row(index) {
        this.invitations.splice(index, 1);
    }

    update_badge() {
        this.badge = Object.keys(this.enrollments).length > 0;
    }
}

Enrol.$inject = ['$location', '$scope', '$rootScope', 'notification', 'user', 'objectproxy', 'socket'];

export default Enrol;
