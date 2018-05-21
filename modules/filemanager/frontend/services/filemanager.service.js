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

/**
 * Created by riot on 10.03.16.
 */

'use strict';

let jsondiffpatch = require('jsondiffpatch').create();

/* TODO:
 * Handle renamed objects
 * Delete objects locally, too
 * Check out search, there's some problems
 * On put, update: Validate first and bail out. Form might already do this, but we should just make sure.
 */

/* old reverse mapping of service:
 obj: objects,
 lists: lists,
 newgetlist: searchItems,
 getlist: getList,
 get: getObject,
 subscribe: subscribeObject,
 unsubscribe: unsubscribeObject,
 put: putObject,
 del: deleteObject
 */

class FileManagerService {
    constructor($q, $socket, $schemata, $rootScope, statusbar) {
        console.log('[FMS] Object proxy service started');
        this.q = $q;
        this.socket = $socket;
        this.schemata = $schemata;
        this.rootscope = $rootScope;
        this.statusbar = statusbar;

        this.requestId = 0;
        this.requests = 0;

        this.lists = {};
        this.callbacks = {};

        this.volumes = {};
        this.directories = {};

        let self = this;

        /*
        this.update_status = function () {
            if (self.requests === 0) {
                self.statusbar.set_status('Ready.')
            } else {
                self.statusbar.set_status(self.requests + ' requests');
            }
        };
        */


        this.getRequestId = function() {
            this.requests += 1;

            return this.requestId++;
        };

        this.signInWatcher = this.rootscope.$on('User.Login', function (ev) {
            self.get_volumes();
        });


        function handleFilemanagerResponse(msg) {
            let data = msg.data;
            let requestId = data.req;

            if (msg.action === 'get_volumes') {
                self.volumes = [];
                for (let item of msg.data.volumes) {
                    console.log(item);
                    item.type = 'folder';
                    self.volumes.push(item);
                }
                console.debug('Volumes after get_volumes:', self.volumes);
            } else if (msg.action === 'get_directory') {
                // 1. get directory root from volumes
                // 2. find node by traversing rest of the path
                // 3. attach all nodes by traversing their path

                console.log('[FMS] Got directory:', msg.data);

            }

            if (angular.isDefined(self.callbacks[requestId])) {
                let callback = self.callbacks[requestId];
                delete self.callbacks[requestId];
                callback.resolve(data);
            } else {
                console.log('[FMS] Filemanager request without callback: ', msg.action, msg.data);
            }
        }

        self.socket.listen('hfos.filemanager.manager', handleFilemanagerResponse);


        this.get_volumes = function () {
            console.log('[FMS] Getting volumes');
            let reqid = self.getRequestId();

            self.socket.send({
                component: 'hfos.filemanager.manager',
                action: 'get_volumes',
                data: {
                    req: reqid
                }
            });

            let deferred = self.q.defer();
            self.callbacks[reqid] = deferred;

            let query = deferred.promise.then(function (response) {
                console.log('[FMS] Get response:', response);
                return response;
            });

            return query;
        };

        this.getDirectory = function(uuid) {
            console.log('[FMS] Clicked on node ', uuid);

            let reqid = self.getRequestId();

            self.socket.send({
                component: 'hfos.filemanager.manager',
                action: 'get_directory',
                data: {
                    uuid: uuid,
                    req: reqid
                }
            });

            let deferred = self.q.defer();
            self.callbacks[reqid] = deferred;

            let query = deferred.promise.then(function (response) {
                console.log('[FMS] Get response:', response);
                return response;
            });

            return query;
        };

        this.getFile = function (uuid) {
            console.log('[FMS] Async-getting object ', schema, uuid);

            let reqid = self.getRequestId();

            self.socket.send({
                component: 'hfos.filemanager.manager',
                action: 'get',
                data: {
                    req: reqid,
                    uuid: uuid
                }
            });

            let deferred = self.q.defer();
            self.callbacks[reqid] = deferred;

            let query = deferred.promise.then(function (response) {
                console.log('[FMS] Get response:', response);
                return response;
            });

            return query;
        };

        this.sendFile = function (file, volume, path) {
            console.log('[FMS] SendFile initiated.');

            let reader = new FileReader();
            let raw = new ArrayBuffer();
            if (typeof path === 'undefined') {
                path = '';
            }

            let reqid = self.getRequestId();

            reader.loadend = function () {
                console.log('[FMS] SendFile: Load end');
            };

            reader.onload = function (e) {
                console.debug('[FMS] SendFile event');
                raw = e.target.result;
                let msg = {
                    component: 'hfos.filemanager.manager',
                    action: 'put',
                    data: {
                        req: reqid,
                        name: file.name,
                        raw: window.btoa(raw),
                        volume: volume,
                        path: path
                    }
                };
                console.debug('[FMS] Sending via socket');
                self.socket.send(msg);
                console.log("[FMS] File has been transferred.");
            };

            reader.readAsBinaryString(file);

            let deferred = self.q.defer();
            self.callbacks[reqid] = deferred;

            let query = deferred.promise.then(function (response) {
                console.log('[FMS] Get response:', response);
                return response;
            });

            return query;

        }

    }

    /*

    subscribe(things) {
        console.log('[FMS] Subscribing to file ', things);
        let data;
        if (typeof things === 'string') {
            data = [things];
        } else {
            data = things;
        }
        this.socket.send({'component': 'hfos.filemanager.manager', 'action': 'subscribe', 'data': data});
    }

    unsubscribe(things) {
        console.log('[FMS] Unsubscribing to object ', things);
        let data;
        if (typeof things === 'string') {
            data = [things];
        } else {
            data = things;
        }
        this.socket.send({'component': 'hfos.filemanager.manager', 'action': 'unsubscribe', 'data': data});
    }

    */

    delete(uuid) {
        console.log('[FMS] Deleting file ', uuid);

        let reqid = this.getRequestId();

        this.socket.send({
            'component': 'hfos.filemanager.manager',
            'action': 'delete',
            'data': {
                'req': reqid,
                'uuid': uuid
            }
        });

        let deferred = this.q.defer();
        this.callbacks[reqid] = deferred;

        let query = deferred.promise.then(function (response) {
            console.log('[FMS] Delete response:', response);
            return response;
        });

        return query;
    }
}

FileManagerService.$inject = ['$q', 'socket', 'schemata', '$rootScope', 'statusbar'];

export default FileManagerService;
