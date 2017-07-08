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

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:EnrolCtrl
 * @description
 * # EnrolCtrl
 * Controller of the hfosFrontendApp
 */
class Enrol {

    constructor(scope, $modal, navdata, user, objectproxy, socket, menu, qr) {
        this.scope = scope;
        this.$modal = $modal;
        this.navdata = navdata;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;
        this.qr = qr;
        
        this.invitations = {
            uuid: {
                name: 'Max Mustermann',
                email: 'max@mustermann.com',
                status: 'Pending'
            },
            other: {
                name: 'Maxine Musterfrau',
                email: 'maxine@musterfrau.de',
                status: 'Accepted'
            },
            another: {
                name: 'Lutz Lorbeer',
                email: 'lutz@lorbeer.de',
                status: 'Denied'
            }
        };
        
        this.verifications = {
            uuid: {
                name: 'Dieter Doofmann',
                email: 'd@doof.de',
                status: 'Open'
            },
            other: {
                name: 'Paul Paule',
                email: 'p@paule.de',
                status: 'Open'
            }
        };
        
        this.new_invitations = [{
            name: '',
            email: ''
        }];
        
        this.verification_counter = 2;
        this.invitation_counter = 2;
    }
    
    invite_by_email() {
        for (let item of this.new_invitations) {
            
            console.log('[ENROL] Inviting user:', item);
            let request = {
                component: 'hfos.enrol.manager',
                action: 'invite',
                data: {
                    name: item.name,
                    email: item.email
                }
            };
            this.socket.send(request);
        }
    }
    
    add_invitation_row() {
        this.new_invitations.push({name: '', email:''});
    }
    
    remove_invitation_row(index) {
        this.new_invitations.splice(index, 1);
    }
}

Enrol.$inject = ['$scope', '$modal', 'navdata', 'user', 'objectproxy', 'socket', 'menu', 'alert'];

export default Enrol;