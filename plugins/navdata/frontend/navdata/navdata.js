'use strict';
/*
 * Hackerfleet Operating System
 * =====================================================================
 * Copyright (C) 2011-2015 riot <riot@hackerfleet.org> and others.
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

    constructor(socket, alert, modal) { //$rootScope, $interval, socket, createDialog, $alert) {
        console.log('NavDataService constructing');
        this.socket = socket;
        this.alert = alert;
        this.modal = modal;

        // this.sock = $websocket('ws://' + host + ':' + port + '/websocket');
        console.log('NavDataService constructed');

    }


}

NavDataService.$inject = ['socket', '$alert', '$modal'];

export default NavDataService;
