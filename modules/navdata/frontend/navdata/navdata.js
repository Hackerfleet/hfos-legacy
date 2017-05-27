'use strict';
/*
 * Hackerfleet Operating System
 * =====================================================================
 * Copyright (C) 2011-2016 riot <riot@c-base.org> and others.
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
 */

/**
 * Created by riot on 21.02.16.
 */


class NavDataService {

    constructor(rootscope, socket, objectproxy, alert, modal, systemconfig) { //$rootScope, $interval, socket, createDialog, $alert) {
        console.log('NavDataService constructing');
        this.rootscope = rootscope;
        this.socket = socket;
        this.op = objectproxy;
        this.alert = alert;
        this.modal = modal;
        this.systemconfig = systemconfig;

        this.vessel = null;
        this.vesseluuid = '';

        console.log('[NAV] NavDataService constructed');

        let self = this;


        this.updateConfig = function() {
            self.op.getObject('vessel', this.vesseluuid, true, {})
        };

        rootscope.$on('OP.Get', function(event, objuuid, obj, schema) {
            if (schema == 'vessel' && obj.uuid == self.vesseluuid) {
                console.log('[NAV] Local vessel info received!');
                self.vessel = obj;
            }
        });

        rootscope.$on('System.Config', function(ev) {
            console.log('[NAV] System config was updated, acquiring new vessel info');
            self.vesseluuid = systemconfig.config.vesseluuid;
            self.updateConfig();
        });

        if (systemconfig.config != null) {
            self.updateConfig();
        }


    }


}

NavDataService.$inject = ['$rootScope', 'socket', 'objectproxy', '$alert', '$modal', 'systemconfig'];

export default NavDataService;
