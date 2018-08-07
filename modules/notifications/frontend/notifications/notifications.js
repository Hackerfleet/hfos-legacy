'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:notificationsCtrl
 * @description
 * # notificationsCtrl
 * Controller of the hfosFrontendApp
 */

class notifications {

    constructor(scope, rootscope, schemata, $modal, user, objectproxy, socket, menu, NgTableParams, common) {
        this.scope = scope;
        this.rootscope = rootscope;
        this.$modal = $modal;
        this.user = user;
        this.op = objectproxy;
        this.socket = socket;
        this.menu = menu;

        this.show_filter = true;
        this.show_columns = false;
        this.show_order = false;

        this.contact_list = [];

        this.cols = [];

        let subdata = {
            lastname: ['n', 'family-name'],
            firstname: ['n', 'given-name'],
            email: ['email', 'value'],
            city: ['adr', 'locality'],
            country: ['adr', 'country-name'],
            organization: ['org', 'organization-name'],
            nickname: ['nickname']
        };

        this.all = Object.keys(subdata);

        this.shown = ['lastname', 'firstname', 'email', 'city', 'country', 'organization'];

        let self = this;

        this.request_notifications = function () {
            console.log('[NOTIFICATIONS] Login successful - fetching contact data');
            this.op.search('contact', '*', '*').then(function (msg) {
                let notifications = msg.data.list;
                console.log("[NOTIFICATIONS] Notifications: ", notifications);
                for (let contact of notifications.data) {
                    let contact_entry = {
                        name: contact.fn,
                        uuid: contact.uuid,
                        dropdown: false
                    };

                    for (let field of Object.keys(subdata)) {
                        let node = contact;
                        for (let path of subdata[field]) {
                            try {
                                node = node[path];
                            } catch (TypeError) {
                                node = null;
                            }
                        }
                        if (node !== null && typeof node !== 'undefined') {
                            contact_entry[field] = node.join(" ");
                        }
                    }
                    console.log('[ROSTER] Pushing contact:', contact_entry);
                    self.contact_list.push(contact_entry);
                }


                self.tableParams = new NgTableParams(
                    {},
                    {
                        dataset: self.contact_list
                    }
                );
            });
        };

        this.update_cols = function () {
            let schema = self.schema.schema.properties;
            self.cols = [];

            for (let field of Object.keys(schema)) {
                let hidden = ['uuid', 'owner', 'uid', 'sort-string'];
                if (hidden.indexOf(field) > 0) {
                    continue;
                }


                if (schema[field].type === 'string') {
                    let title = schema[field].title || field.charAt(0).toUpperCase() + field.substr(1);
                    let filter = {};
                    filter[field] = 'text';

                    if (self.all.indexOf(field) < 0 && hidden.indexOf(field) < 0) {
                        self.all.push(field);
                    }
                    let column = {
                        field: field,
                        title: title,
                        show: self.shown.indexOf(field) > 0,
                        sortable: field,
                        filter: filter
                    };
                    self.cols.push(column);
                }
            }

            for (let field of Object.keys(subdata)) {
                let title = field.charAt(0).toUpperCase() + field.substr(1);
                let filter = {};
                filter[field] = 'text';
                let column = {
                    field: field,
                    title: title,
                    show: self.shown.indexOf(field) >= 0,
                    sortable: field,
                    path: subdata[field],
                    filter: filter
                };
                self.cols.push(column);
            }
            console.log('[ROSTER] Columns:', self.cols);
        };


        this.move_column = function(column, currentIdx, value) {
            let newPosition = currentIdx + value;
            if (newPosition >= self.cols.length || newPosition < 0) {
                return;
            }
            self.cols[currentIdx] = self.cols[newPosition];
            self.cols[newPosition] = column;
        };

        self.scope.$on('$destroy', function () {
        });

        //self.socket.listen('hfos.auth.login', self.request_notifications);

        this.loginupdate = this.rootscope.$on('User.Login', function () {
            console.log('[ROSTER] Just Logged in, getting notifications');
            self.request_notifications();
        });

        if (this.user.signedin === true) {
            console.log('[ROSTER] Logged in, getting notifications');
            self.schema = schemata.get('contact');
            self.request_notifications();
            self.update_cols();
        }

        self.rootscope.$on('Schemata.Update', function () {
            self.schema = schemata.get('contact');
            console.log('SCHEMA:', self.schema);
            self.update_cols();
        })
    }
}

notifications.$inject = ['$scope', '$rootScope', 'schemata', '$modal', 'user', 'objectproxy', 'socket', 'menu', 'NgTableParams'];

export default notifications;
