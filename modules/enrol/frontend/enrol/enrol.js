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

import deletionWarning from './modals/deletionWarning.tpl.html';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:EnrolCtrl
 * @description
 * # EnrolCtrl
 * Controller of the hfosFrontendApp
 */
class Enrol {

    constructor($location, scope, rootscope, notification, user, objectproxy, socket, modal, timeout) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.notification = notification;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.modal = modal;
        this.timeout = timeout;


        // TODO: Fix the url. Needs to be constructed from the public/internal hostname, should be switchable in ui
        this.invite_url = $location.protocol() + '://' + $location.host() + ":" + $location.port() + '/#!/invitation/';
        this.invitations = [{
            name: '',
            email: ''
        }];

        this.filter_string = null;

        this.users = {};
        this.checked_users = {};
        this.all_users = false;
        this.action_users = '';

        this.enrollments = {};
        this.checked_enrollments = {};
        this.all_enrollments = false;
        this.action_enrollments = '';

        this.enrollment_badge = false;
        this.user_badge = false;

        let self = this;

        this.getter_timeout = null;

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
                    self.update_enrollment_badge();
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
                self.update_enrollment_badge();
            } else if (['addrole', 'delrole', 'delete', 'toggle'].indexOf(msg.action) >= 0) {
                console.log('[ENROL] Action');
                if (msg.action === 'delete') {
                    if (msg.data[0] === true) {
                        delete self.users[msg.data[1]];
                    }
                } else {
                    if (self.getter_timeout !== null) self.timeout.cancel(self.getter_timeout);
                    self.getter_timeout = self.timeout(self.get_data, 1000);
                }
            } else {
                console.log('[ENROL] Unkown action:', msg.action, msg.data);
            }
        });

        this.get_data = function () {
            console.log('[ENROL] Getting data');
            self.op.search('enrollment', '*', '*').then(function (msg) {
                let enrollments = msg.data.list;
                console.log('[ENROL] Data received:', enrollments);

                for (let enrollment of enrollments) {
                    self.enrollments[enrollment.uuid] = enrollment;
                }
                self.update_enrollment_badge();
            });
            self.op.search('user', '*', '*').then(function (msg) {
                let users = msg.data.list;
                console.log('[ENROL] Data received:', users);

                for (let user of users) {
                    self.users[user.uuid] = user;
                }
                self.update_user_badge();
            });
            self.timeout.cancel(self.getter_timeout);
            self.getter_timeout = null;
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
                self.update_enrollment_badge();
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


    toggle_users() {
        let self = this;
        function filtered(user) {
            if (self.filter_string === null) return true;

            let name = user.name,
                mail = user.mail;

            return (typeof name !== 'undefined' && name.indexOf(self.filter_string) >= 0) ||
                   (typeof mail !== 'undefined' && user.mail.indexOf(self.filter_string) >= 0);
        }

        for (let uuid of Object.keys(this.users)) {
            if (filtered(this.users[uuid])) this.checked_users[uuid] = this.all_users;
        }
    }

    act_users() {
        this.deletion_candidates = [];

        for (let uuid of Object.keys(this.checked_users)) {
            if (this.checked_users[uuid] === true) {
                if (this.action_users === 'Delete') {
                    this.deletion_candidates.push(uuid);
                } else if (this.action_users === 'Deactivate') {
                    this.toggle_user(uuid, false)
                } else if (this.action_users === 'Activate') {
                    this.toggle_user(uuid, true)
                }
            }
        }

        if (this.action_users === 'Delete' && this.deletion_candidates.length > 0) {
            this.modal({
                template: deletionWarning,
                scope: this.scope,
                title: 'Really delete users?',
                keyboard: false,
                id: 'deletionWarningDialog'
            });
        } else {
            this.action_users = null;
            this.checked_users = {};
            this.all_users = false;
        }
    }

    delete_user(uuid) {
        this.deletion_candidates = [uuid];

        this.modal({
            template: deletionWarning,
            scope: this.scope,
            title: 'Really delete user?',
            keyboard: false,
            id: 'deletionWarningDialog'
        });
    }


    confirm_deletion() {
        for (let uuid of this.deletion_candidates) {
            console.log('Deleting user ', uuid);
            let request = {
                component: 'hfos.enrol.manager',
                action: 'delete',
                data: uuid
            };

            this.socket.send(request);
        }

        this.deletion_candidates = [];
        this.checked_users = {};
        this.all_users = false;
        this.action_users = null;
    }

    toggle_user(uuid, status) {
        console.log('Toggling user activation', uuid);
        let request = {
            component: 'hfos.enrol.manager',
            action: 'toggle',
            data: {
                uuid: uuid,
                status: status
            }
        };
        this.socket.send(request);
    }

    add_role(role, uuid) {
        console.log('Adding role to user', role, uuid);
        let request = {
            component: 'hfos.enrol.manager',
            action: 'addrole',
            data: {
                uuid: uuid,
                role: role
            }
        };
        this.socket.send(request);
    }

    remove_role(role, uuid) {
        console.log('Removing role from user', role, uuid);
        let request = {
            component: 'hfos.enrol.manager',
            action: 'delrole',
            data: {
                uuid: uuid,
                role: role
            }
        };
        this.socket.send(request);
    }

    update_enrollment_badge() {
        this.enrollment_badge = Object.keys(this.enrollments).length > 0;
    }

    update_user_badge() {
        this.user_badge = Object.keys(this.users).length > 0;
    }
}

Enrol.$inject = ['$location', '$scope', '$rootScope', 'notification', 'user', 'objectproxy', 'socket', '$modal', '$timeout'];

export default Enrol;
