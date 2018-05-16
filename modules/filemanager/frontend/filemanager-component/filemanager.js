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

    constructor(filemanagerservice, userservice, $state, socket, $scope, $rootScope, $timeout, notification) {
        this.filemanagerservice = filemanagerservice;
        this.state = $state;
        this.user = userservice;
        this.socket = socket;
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.notification = notification;

        this.signedin = false;

        this.changetimeout = null;
        this.gridChangeWatcher = null;

        this.lockState = false;

        console.log('[FILES] FileManager initializing with Profile: ', userservice.profile);
        //console.log(userservice.profile);

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
            self.filemanagerservice.get_volumes().then(function (data) {
                console.log('[FM] Response for get_volumes:', data);
                self.nodes = self.filemanagerservice.volumes;
            })
        };


        this.signInWatcher = this.rootscope.$on('User.Login', function (ev) {
            self.get_volumes();
        });

        this.click_node = function (uuid) {
            console.log('[FM] Clicked on node ', uuid);
            this.filemanagerservice.getDirectory(uuid).then(function (data) {
                console.log('[FM] Inserting directory content');

                let volume = null;

                for (let i in self.filemanagerservice.volumes) {
                    if (data.volume === i.uuid) {
                        volume = i;
                    }
                }

                let split_path = data.path.split('/');

                console.log('[FM] Split Path:', split_path);
                for (let path in split_path) {
                    let new_node = self.nodes[path]
                }
            });
        };

        this.click_file = function (uuid) {
            console.log('[FM] Clicked on file ', uuid);
        };

        if (self.user.signedin) {
            this.get_volumes();
        }
    }

}


fileManager.$inject = ['filemanagerservice', 'user', '$state', 'socket', '$scope', '$rootScope', '$timeout', 'notification'];

export default fileManager;
