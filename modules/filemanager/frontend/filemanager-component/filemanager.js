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

class fileManager {

    constructor(userservice, $state, socket, $scope, $rootScope, $timeout, notification) {
        this.signedin = false;
        this.state = $state;
        this.user = userservice;
        this.socket = socket;
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.notification = notification;

        this.changetimeout = null;
        this.gridChangeWatcher = null;

        this.lockState = false;

        console.log('[FILES] FileManager initializing with Profile: ', userservice.profile);
        console.log(userservice.profile);

        this.nodes = [
            {
                "uuid": 1,
                "name": "node1",
                "type": "folder",
                "path": "foo",
                "nodes": [
                    {
                        "uuid": 11,
                        "name": "node1.1",
                        "type": "folder",
                        "path": "foo/bar",
                        "nodes": [
                            {
                                "uuid": 111,
                                "name": "node1.1.1",
                                "nodes": [],
                                "path": "foo/bar/file",
                                "type": "file"
                            }
                        ]
                    },
                    {
                        "uuid": 12,
                        "name": "node1.2",
                        "nodes": [],
                        "path": "foo/bar/qux",
                        "type": "file"
                    }
                ]
            },
            {
                "uuid": 2,
                "name": "node2",
                "type": "folder",
                "nodrop": true,
                "nodes": [
                    {
                        "uuid": 21,
                        "name": "node2.1",
                        "nodes": [],
                        "type": "file"
                    },
                    {
                        "uuid": 22,
                        "name": "node2.2",
                        "nodes": [],
                        "type": "file"
                    }
                ]
            },
            {
                "uuid": 3,
                "name": "node3",
                "type": "folder",
                "nodes": [
                    {
                        "uuid": 31,
                        "name": "node3.1",
                        "nodes": [],
                        "type": "file"
                    }
                ]
            }
        ];

        let self = this;

        this.get_volumes = function () {
            console.log('[FM] Getting volumes');
            let request = {
                component: 'hfos.filemanager.manager',
                action: 'get_volumes',
                data: null
            };
            self.socket.send(request);
        };

        this.signInWatcher = this.rootscope.$on('User.Login', function (ev) {
            self.get_volumes();
        });

        this.socket.listen('hfos.filemanager.manager', function(msg) {
            if (msg.action === 'get_volumes') {
                self.nodes = [];
                for (let item of msg.data) {
                    console.log(item);
                    item.type = 'folder';
                    self.nodes.push(item);
                }
                console.log('Nodes after get_volumes:', self.nodes);
            } else if (msg.action === 'get_directory') {
                // 1. get directory root from volumes
                // 2. find node by traversing rest of the path
                // 3. attach all nodes by traversing their path
            }
        });

        this.click_node = function (uuid) {
            console.log('[FM] Clicked on node ', uuid);
            let packet = {
                component: 'hfos.filemanager.manager',
                action: 'get_directory',
                data: uuid
            };
            self.socket.send(packet);
        };

        this.click_file = function (uuid) {
            console.log('[FM] Clicked on file ', uuid);
        };

        if (self.user.signedin) {
            self.get_volumes();
        }
    }

}


fileManager.$inject = ['user', '$state', 'socket', '$scope', '$rootScope', '$timeout', 'notification'];

export default fileManager;
