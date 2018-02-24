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
 * @name hfosFrontendApp.controller:PasswordChangeCtrl
 * @description
 * # PasswordChangeCtrl
 * Controller of the hfosFrontendApp
 */
class PasswordChange {

    constructor(scope, user, socket) {
        this.scope = scope;
        this.user = user;
        this.socket = socket;

        this.password_old = '';
        this.password_new = '';
        this.password_confirm = '';
    }

    update_password() {
        this.changePassword(this.password_old, this.password_new, this.password_confirm);
    }

    changePassword(old, new_password, confirm_password) {
        if (this.user.has_password && (typeof old === 'undefined' || old === '')) {
            console.log('Has old password but it was not supplied!');
            return
        }

        if (new_password !== confirm_password) {
            console.log("Unexpected: New passwords don't match!");
            return
        }
        console.log('Transmitting password change request');
        let packet = {
            component: 'hfos.enrol.manager',
            action: 'changepassword',
            data: {
                'old': old,
                'new': new_password
            }
        };
        this.socket.send(packet);
    }

}

PasswordChange.$inject = ['$scope', 'user', 'socket'];

export default PasswordChange;
