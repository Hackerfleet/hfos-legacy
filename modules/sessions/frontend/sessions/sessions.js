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

class Sessions {

    constructor(scope, rootscope, user, socket, notification, schemata, objectproxy) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.user = user;
        this.socket = socket;
        this.notification = notification;
        this.schemata = schemata;
        this.op = objectproxy;

        this.form = null;
        this.schema = null;
        this.model = null;
        this.editing = false;

        this.sessions = {};

        let self = this;

        this.get_sessions = function () {
            console.log('[SESSIONS] Login successful - fetching session data');

            self.op.search('session', {owner: self.user.uuid}, '*').then(function (msg) {
                if (typeof msg.data.list !== 'undefined') {
                    self.sessions = {};
                    for (let session of msg.data.list){
                        self.sessions[session.uuid] = session;
                    }
                } else {
                    self.sessions = {};
                }
            });
        };

        this.get_user_data = function () {
            console.log('[SESSIONS] Getting user data');

            self.model = {};

            self.get_sessions();

            if (schemata.schemata !== null) {
                self.get_schema();
            }

        };

        this.get_schema = function () {
            console.log('[SESSIONS] Requesting schema');
            self.schema = self.schemata.schema('session');
            self.form = self.schemata.form('session');
        };


        if (user.signedin === true) {
            this.get_user_data();
        }

        let schemaHandler = this.rootscope.$on('Schemata.Update', function () {
            console.log('[SESSIONS] Getting schema');
            self.get_schema();
        });

        let loginHandler = this.rootscope.$on('User.Login', function () {
            console.log('[SESSIONS] Logged in, getting user data');
            self.get_user_data();
        });

        this.scope.$on('$destroy', function () {
            console.log('[SESSIONS] Destroying');
            loginHandler();
            schemaHandler();
        });
    }

    uploadFile() {
        console.log('[SESSIONS] Uploading attachment');
        let file = document.getElementById('upload_file').files[0];
        let self = this;

        this.op.sendFile(file, 'hfos.sessions').then(function (result) {
            console.log('[SESSIONS] Uploaded. Result:', result);

            if (result.success === true) {
                self.model.files.push({
                    uuid: result.uuid,
                    filename: result.filename
                });

                self.notification.add('success', 'File attached', 'Your file has been uploaded successfully.', 5);
            } else {
                self.notification.add('danger', 'Upload failed', 'The attachment was not uploaded successfully:' + result.reason, 10);
            }

        })
    }

    submitSession() {
        let model = this.model;
        let self = this;
        if (this.editing !== true) { model.uuid = 'create'; }

        console.log('[SESSIONS] Object update initiated with ', model);
        this.op.put('session', model).then(function (result) {
            if (typeof result.uuid !== 'undefined') {
                self.notification.add('success', 'Submission stored', 'Your session has been submitted successfully.', 5);
                self.get_sessions();
            } else {
                self.notification.add('warning', 'Submission not stored', 'Your session has not been submitted: ' + result.reason, 10);
            }
        });
    }

    deleteSession(uuid) {
        let self = this;

        console.log('[SESSIONS] Requesting session deletion: ', uuid);
        this.op.deleteObject('session', uuid).then(function (result) {
            if (typeof result.uuid !== 'undefined') {
                self.notification.add('success', 'Submission deleted', 'Your session has been deleted successfully.', 5);
                delete self.sessions[uuid];
            } else {
                self.notification.add('warning', 'Submission not deleted', 'Your session has not been deleted: ' + result.reason, 10);
            }
        });
    }

    editSession(uuid) {
        console.log('[SESSIONS] Editing session:', uuid);
        this.model = this.sessions[uuid];
        this.editing = true;
    }

    addSession() {
        console.log('[SESSIONS] Adding a new session');
        this.model = {};
        this.editing = false;
        document.getElementById('upload_file').value = '';

    }
}

Sessions.$inject = ['$scope', '$rootScope', 'user', 'socket', 'notification', 'schemata', 'objectproxy'];

export default Sessions;
