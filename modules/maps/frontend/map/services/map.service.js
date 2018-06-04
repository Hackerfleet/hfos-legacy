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

class MapService {

    constructor($rootScope, user, op, socket, schemata, notification, navdata) {
        this.scope = $rootScope;
        this.user = user;
        this.op = op;
        this.socket = socket;
        this.schemata = schemata;
        this.notification = notification;
        this.navdata = navdata;

        this.mapviews = {};
        this.geoobjects = {};
        this.layergroups = {};
        this.other_layers = {};
        this.all_layers = {};

        this.layers = {
            baselayers: {},
            overlays: {},
            geolayers: {},
        };

        this.default_color = 'red';
        this.default_marker = "poi";
        this.default_path = "route";
        this.default_shape = "danger";

        this.default_custom_marker = "Custom";
        this.default_custom_path = "Custom";
        this.default_custom_shape = "Custom";

        this.default_options = {
            marker: {
                poi: 'Point of interest',
                waypoint: 'Waypoint',
                custom: 'Custom'
            },
            path: {
                route: 'Route',
                vessel_trail: 'Vessel trail',
                custom: 'Custom'
            },
            shape: {
                danger: 'Dangerous zone',
                traffic: 'Traffic separation zone',
                industry: 'Industrial zone',
                fishing: 'Fishing zone',
                custom: 'Custom'
            }
        };

        this.offline_loader = false;
        this.offline_loader_queue = {};
        this.offline_loader_zoom = 2;

        let self = this;

        /****************************************************************/


        /********** Map Tile Service *********/

        this.get_offline_data = function (extent, zoom, layers) {
            console.log('[MAPSVC] Requesting extent for offline use');
         
            let event = {
                component: 'hfos.map.maptileservice',
                action: 'request_maptile_area',
                data: {
                    extent: extent,
                    zoom: zoom,
                    layers: layers
                }
            };
            self.socket.send(event);
        };

        this.hasQueued = function () {
            return Object.keys(self.offline_loader_queue).length > 0
        };

        this.queue_trigger = function (uuid) {
            console.log('[MAPSVC] Requesting download of queue', uuid);
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_trigger',
                'data': uuid
            };
            self.socket.send(event);
        };
        this.queue_cancel = function () {
            console.log('[MAPSVC] Requesting cancellation of queues');
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_cancel'
            };
            self.socket.send(event);
        };
        this.queue_remove = function (uuid) {
            console.log('[MAPSVC] Requesting removal of queue', uuid);
            let event = {
                'component': 'hfos.map.maptileservice',
                'action': 'queue_remove',
                'data': uuid
            };
            self.socket.send(event);
        };
        
        function handle_maptileservice(msg) {
            if (msg.action === 'queued') {
                console.log('[MAPSVC] Loader request was queued');
                self.offline_loader_queue[msg.data.uuid] = msg.data;
            } else if (msg.action === 'empty') {
                console.log('[MAPSVC] No tiles to fetch');
                self.notification.add('warning', 'No tiles to fetch', 'The area you selected does not contain any tile data.')
            } else if (msg.action === 'acting') {
                self.offline_loader_queue[msg.data].acting = true;
                self.notification.add('success', 'Caching tiles', 'The system tries to download the requested tiles now.')
            } else if (msg.action === 'offline_loader_progress') {
                self.offline_loader_queue[msg.data.queue].completed = msg.data.completed;
            } else if (msg.action === 'removed') {
                delete self.offline_loader_queue[msg.data.uuid];
            }
        }
        this.socket.listen('hfos.map.maptileservice', handle_maptileservice);
    }


    gdal_upload() {
        console.log('Uploading new map file.');

        let file = document.getElementById('filename').files[0];
        console.log('file: ', file);
        this.socket.sendFile(file, 'hfos.map.gdal', 'mapimport');

    }

    gdal_rescan() {
        console.log('Triggering rastertile path rescan.');

        this.socket.send({
            component: 'hfos.map.gdal',
            action: 'rescan'
        });

    }
}

MapService.$inject = ['$rootScope', 'user', 'objectproxy', 'socket', 'schemata', 'notification', 'navdata'];

export default MapService;