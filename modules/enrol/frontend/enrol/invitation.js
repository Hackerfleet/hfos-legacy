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
 * @name hfosFrontendApp.controller:AcceptCtrl
 * @description
 * # AcceptCtrl
 * Controller of the hfosFrontendApp
 */
class Accept {
    
    constructor(scope, rootScope, socket, $stateParams, $timeout) {
        this.scope = scope;
        this.rootscope = rootScope;
        this.socket = socket;
        this.stateParams = $stateParams;
        this.timeout = $timeout;
        
        this.uuid = null;
        this.success = false;
        this.error = false;
        this.status = false;
    }
    
    $onInit() {
        if (typeof this.stateParams.uuid !== 'undefined') {
            this.uuid = this.stateParams.uuid;
        }
        
        console.log('[INVITATION] UUID:', this.uuid);
        
        let packet = {
            component: 'hfos.enrol.enrolmanager',
            action: 'accept',
            data: this.uuid
        };
        let self = this;
        this.rootscope.$on('Client.Connect', function () {
            self.timeout(function () {
                self.socket.send(packet);
            }, 3000);
        });
        this.socket.listen('hfos.enrol.enrolmanager', function(msg) {
            console.log('Message!', msg);
            if (msg.action === 'accept') {
                let data = msg.data[true];
                console.log(data);
                if (typeof data === 'undefined') {
                    self.error = true;
                } else {
                    self.status = data;
                    self.success = true;
                }
            }
        });
    }
}

Accept.$inject = ['$scope', '$rootScope', 'socket', '$stateParams', '$timeout'];

export default Accept;
