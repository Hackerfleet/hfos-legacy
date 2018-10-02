'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TaskGridCtrl
 * @description
 * # TaskGridCtrl
 * Controller of the hfosFrontendApp
 */

import deletionWarning from './modals/deletionWarning.tpl.html'

class taskgridcomponent {
    constructor($scope, $rootScope, $timeout, user, ObjectProxy, state, menu,
                notification, modal, NgTableParams, $stateParams) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;
        this.menu = menu;
        this.notification = notification;
        this.modal = modal;
        $scope.stateParams = $stateParams;

        this.config = {};

        this.columns = {};
        this.columnsize = 4;

        this.tasklist = {};

        this.taskgridconfig = {};
        this.taskgridconfiguuid = "";
        this.taskgroups = {};
        this.tasksByGroup = {};

        this.taskgrids = [];
        this.projects = {};
        this.tags = {};

        this.filter_tag = "";
        this.filter_project = "";

        this.selected_task = null;

        this.show_filters = false;
        this.show_filters_tag = false;
        this.show_filters_project = false;

        this.selected = [];
        this.selected_groups = [];

        this.me_target_group = null;
        this.me_tag = null;
        this.me_project = null;
        this.me_priority = null;

        this.search_string = '';

        this.changetimeout = null;
        this.lockState = false;
        this.side_bar_open = false;

        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 100,
            rowHeight: 100,
            colWidth: 100,
            // mobileBreakPoint: 200,
            mobileModeEnabled: false, // whether or not to toggle mobile mode when screen width is less than mobileBreakPoint

            draggable: {
                enabled: false
            },
            resizable: {
                enabled: false
            }
        };

        let self = this;

        this.tableParams = new NgTableParams({}, {
            getData: function (params) {
                // ajax request to api
                let filter = params._params.filter;

                if (typeof filter === 'undefined') {
                    filter = {'owner': self.user.useruuid};
                }

                if (filter.hasOwnProperty('name')) {
                    filter = {'name': {'$regex': ".*" + filter.name + ".*"}}
                }

                console.log("TASK_TABLE1:", params);
                let limit = params._params.count;
                let skip = limit * (params._params.page - 1);

                return self.op.search('task', filter, '*', null, false, limit, skip).then(function (msg) {
                    let tasks = msg.data.list;
                    params.total(msg.data.size); // recal. page nav controls
                    console.log("TASK_TABLE2:", params);

                    return tasks;
                });
            }
        });

        this.select_task = function (uuid) {
            this.selected_task = uuid;
            this.scope.$broadcast('Changed.UUID', {eid: 'taskEditor', uuid: self.selected_task});
            if (!this.side_bar_open) {
                this.open_sidebar();
            }
        };

        this.open_sidebar = function () {
            this.scope.$broadcast('Resize', '75%');
            this.side_bar_open = true;
        };

        this.close_sidebar = function () {
            this.scope.$broadcast('Resize', '99%');
            this.side_bar_open = false;
        };

        this.switchtaskgridconfig = function (uuid) {
            console.log('[TASKGRID] Switching taskgrid:', uuid);
            self.taskgridconfiguuid = uuid;

            self.tasklist = [];
            self.tasksByGroup = {};

            self.gettaskgridconfig();
            /*
            self.op.get('taskgridconfig', uuid).then(function(msg) {
                if (msg.action !== 'fail') { */
                    self.state.go('app.taskgrid', {taskgrid: uuid}, {
                        location: 'replace',
                        inherit: false,
                        notify: false
                    });/*
                } else {
                    console.log('[TASKGRID] Could not get taskgrid:', msg);
                }
            });*/
        };

        this.storeTaskGridConfig = function () {
            console.log('[TASKGRID] Pushing taskgridconfig');

            for (let card of self.taskgridconfig.cards) {
                delete card['$$hashKey'];
            }
            self.op.put('taskgridconfig', self.taskgridconfig).then(function (msg) {
                console.log('[TASKGRID] Taskgrid stored');
            });

            self.changetimeout = null;
        };

        this.handleGridChange = function (newVal, oldVal) {
            if (newVal === oldVal) {
                console.log('No actual change');
                return;
            }
            if (self.changetimeout !== null) {
                self.timeout.cancel(self.changetimeout);
            }
            self.changetimeout = self.timeout(self.storeTaskGridConfig, 2000);
        };

        this.gridChangeWatcher = null;

        if (typeof user.clientconfig.taskgridconfiguuid !== 'undefined') {
            this.gettaskgridconfig();
        }

        /*this.scope.$on('OP.Get', function (event, uuid, object, schema) {
            if (uuid === self.taskgridconfiguuid) {
                self.taskgridconfig = object;

                for (let group of self.taskgridconfig.cards) {
                    console.log('Getting taskgroup:', group);
                    self.op.getObject('taskgroup', group.taskgroup);
                }
            } else if (schema === 'taskgroup') {
                console.log('Getting tasksByGroup for taskgroup:', object);
                self.taskgroups[object.uuid] = object;
                self.op.search('task', {taskgroup: object.uuid}, '*').then(function (msg) {
                    let tasks = msg.data.list;
                    self.tasksByGroup[object.uuid] = [];
                    for (let task of tasks) {
                        let visualTask = task;
                        visualTask.showDescription = false;
                        self.tasksByGroup[object.uuid].push(visualTask);
                        self.tasklist[task.uuid] = task;
                    }
                });
            }
        });
        */
    }

    $onInit() {
        let self = this;
        let taskgrid = null;


        console.log('[TASKGRID] STATEPARAMS: ', this.state.params);
        console.log('[TASKGRID] This:', this);
        console.log('[TASKGRID] Scope:', this.scope);

        //console.log('[TASKGRID] Stateparam:', this.scope.state.params.taskgrid);

        if (typeof this.state.params.taskgrid !== 'undefined') {
            console.log('[TASKGRID] Getting params from stateparams');
            taskgrid = this.state.params.taskgrid;

            /*
                projects: this.scope.stateParams.projects,
                tags: this.scope.stateParams.tags
            };*/
            console.log('[TASKGRID] Resulting config:', taskgrid);

        } else {
            console.log("[TASKGRID] WIP! Getting params from scope:", this.scope.initial, this.initial);
            /* Work in progress!
            this.config = {
                taskgrid: this.project.taskgrid,
                projects: this.scope.stateParams.projects,
                tags: this.scope.stateParams.tags
            };

            console.debug('[TASKGRID] Configuration: ', this.config);
            */
        }

        if (taskgrid !== null) {
            this.taskgridconfiguuid = taskgrid;
        } else {
            this.taskgridconfiguuid = this.user.getModuleDefault('taskgriduuid');
        }

        if (this.user.signedin === true) {
            console.log('[TASKGRID] Logged in - fetching taskgridconfig data');
            this.gettaskgridconfig();
        }

        let login_watcher = this.rootscope.$on('User.Login', function () {
            console.log('[TASKGRID] Login successful - fetching taskgridconfig data');
            self.gettaskgridconfig();
        });

        let client_watcher = this.rootscope.$on('Clientconfig.Update', function () {
            self.gettaskgridconfig();
        });

        this.scope.$on('$destroy', function () {
            console.log('[TASKGRID] Destroying');
            login_watcher();
            client_watcher();
        });


    }

    toggleLock() {
        this.lockState = !this.lockState;
        this.gridsterOptions.draggable.enabled = this.lockState;
        this.gridsterOptions.resizable.enabled = this.lockState;
        if (this.lockState) {
            console.log('Enabling gridwatcher');
            this.gridChangeWatcher = this.scope.$watch('$ctrl.taskgridconfig.cards', this.handleGridChange, true);
        } else {
            this.gridChangeWatcher();
        }
    }

    gettaskgridconfig() {
        let self = this;

        console.log('[TASKGRID] Getting data');

        this.op.search('project').then(function (msg) {
            console.log('[TASKGRID] Projects received: ', msg);
            let projects = msg.data.list;
            for (let project of projects) {
                self.projects[project.uuid] = project;
            }
        });

        this.op.search('tag', '', '*').then(function (msg) {
            console.log('[TASKGRID] Tags received: ', msg);
            let tags = msg.data.list;
            for (let tag of tags) {
                self.tags[tag.uuid] = tag;
            }
        });

        this.op.search('taskgridconfig', '', '*').then(function(msg) {
            console.log('[TASKGRID] Grids received: ', msg);
            self.taskgrids = msg.data.list;
        });

        console.log('[TASKGRID] Config: ', this.taskgridconfiguuid);
        this.op.get('taskgridconfig', this.taskgridconfiguuid).then(function(msg) {
            self.taskgridconfig = msg.data.object;
            console.log('[TASKGRID] Grid: ', self.taskgridconfig);

            console.log('[TASKGRID] Getting groups');

            let taskgroups = [];
            for (let card of self.taskgridconfig.cards) {
                taskgroups.push(card.taskgroup);
            }

            self.op.search('taskgroup', {uuid: {'$in': taskgroups}}, '*').then(function(msg) {
                for (let group of msg.data.list) {
                    self.taskgroups[group.uuid] = group;
                }
            });

            console.log('[TASKGRID] Getting tasks');

            self.op.search('task', {taskgroup: {'$in': taskgroups}}, '*').then(function (msg) {
                let tasks = msg.data.list;

                for (let task of tasks) {
                    let visualTask = task;
                    visualTask.showDescription = false;
                    if (typeof self.tasksByGroup[task.taskgroup] === 'undefined') {
                        self.tasksByGroup[task.taskgroup] = [];
                    }
                    self.tasksByGroup[task.taskgroup].push(visualTask);
                    self.tasklist[task.uuid] = task;
                }
            });

        });
    }

    new_task(group_uuid) {
        console.log('[TASKGRID] Adding new task to group:', group_uuid);
        this.state.go('app.editor', {schema: 'task', action: 'create', initial: {taskgroup: group_uuid}})
    }

    select_all() {
        this.selected = [];
        for (let uuid of Object.keys(this.tasklist)) {
            let task = this.tasklist[uuid];

            if (typeof this.search_string !== 'undefined' && this.search_string !== '') {

                let search = this.search_string.toLowerCase(),
                    name = "",
                    description = "";

                if (typeof task.name !== 'undefined') name = task.name.toLowerCase();
                if (typeof task.description !== 'undefined') description = task.description.toLowerCase();

                console.log('[TASKGRID] Filters:', name, description, search);

                if ((name.indexOf(search) > -1 || description.indexOf(search) > -1) &&
                    (this.show_filters_project ? this.filter_project === task.project : true) &&
                    ((this.show_filters_tag ? task.tags.indexOf(this.filter_tag) > -1 : true) ||
                        (this.show_filters_tag && this.filter_tag === '' && task.tags.length === 0))
                ) {
                    this.selected.push(task.uuid);
                }
            } else {
                this.selected.push(task.uuid);
            }
        }
    }


    select_all_of_group(uuid) {
        let index = this.selected_groups.indexOf(uuid);

        if (index < 0) {
            for (let task of this.tasksByGroup[uuid]) {
                if (this.selected.indexOf(task.uuid) < 0) this.selected.push(task.uuid);
            }
            this.selected_groups.push(uuid);
        } else {
            for (let task of this.tasksByGroup[uuid]) {
                this.selected.splice(this.selected.indexOf(task.uuid), 1);
            }
            this.selected_groups.splice(index, 1)
        }
    }

    add_tags() {
        if (typeof this.me_tag === 'undefined' || this.me_tag === null || this.me_tag === '') {
            this.notification.add('warning', 'Select a tag first', 'You have to select a tag to add.', 3);
            return
        }

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            console.log(task);

            if (task.tags.indexOf(this.me_tag) < 0) {
                console.log('[TASKGRID] Adding tag.');
                task.tags.push(this.me_tag);

                this.op.changeObject('task', uuid, {field: 'tags', value: task.tags});
            }
        }
    }

    remove_tags() {
        if (typeof this.me_tag === 'undefined' || this.me_tag === null || this.me_tag === '') {
            this.notification.add('warning', 'Select a tag first', 'You have to select a tag to be removed.', 3);
            return
        }

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];

            if (task.tags.indexOf(this.me_tag) >= 0) {
                task.tags.splice(task.tags.indexOf(this.me_tag), 1);
                this.op.changeObject('task', uuid, {field: 'tags', value: task.tags});
            }
        }
    }


    assign_project() {
        if (typeof this.me_project === 'undefined' || this.me_project === null || this.me_project === '') {
            this.notification.add('warning', 'Select a project first', 'You have to select a project to assign to', 3);
            return
        }

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];

            task.project = this.me_project;
            this.op.changeObject('task', uuid, {field: 'project', value: this.me_project});
        }
    }

    remove_project() {
        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            task.project = '';
            this.op.changeObject('task', uuid, {field: 'project', value: ''});
        }
    }

    set_priority() {
        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            task.priority = this.me_priority;
            this.op.changeObject('task', uuid, {field: 'priority', value: this.me_priority});
        }
    }

    delete_selected() {
        this.modal({
            template: deletionWarning,
            scope: this.scope,
            title: 'Really delete tasks?',
            keyboard: false,
            id: 'deletionWarningDialog'
        });
    }

    confirm_deletion() {
        let self = this,
            success = false;


        for (let uuid of this.selected) {
            console.log('Deleting ticket ', uuid);
            this.op.deleteObject('task', uuid).then(function (response) {
                if (response.data.uuid === uuid) {
                    let task = self.tasklist[uuid];
                    let group = self.tasksByGroup[task.taskgroup];
                    group.splice(group.indexOf(task), 1);
                    delete self.tasklist[uuid];
                    success = true;
                }
            });
        }

        if (success === true) self.notification.add('success', 'Deleted', 'The selected tasks have been deleted.', 3);

        this.selected = [];
    }


    move() {
        if (typeof this.me_target_group === 'undefined' || this.me_target_group === null || this.me_target_group === '') {
            this.notification.add('warning', 'Select a target group', 'You have to select a target group to mass move tasks.', 3);
            return
        }

        console.log('[TASKGRID] Moving Tasks');

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            let old_group = this.tasksByGroup[task.taskgroup];

            old_group.splice(old_group.indexOf(task), 1);

            this.tasksByGroup[this.me_target_group].push(task);

            task.taskgroup = this.me_target_group;

            this.op.changeObject('task', uuid, {'field': 'taskgroup', 'value': this.me_target_group});
        }
    }

    onDropComplete(task, ev, newgroup) {
        if (task === null) {
            return
        }

        console.log('DropComplete: ', task, ev, newgroup);
        let oldgroup = this.tasksByGroup[task.taskgroup];
        oldgroup.splice(oldgroup.indexOf(task), 1);
        task.taskgroup = newgroup;

        this.tasksByGroup[newgroup].push(task);

        this.op.changeObject('task', task.uuid, {'field': 'taskgroup', 'value': newgroup});
    }


}

taskgridcomponent.$inject = [
    '$scope', '$rootScope', '$timeout', 'user', 'objectproxy', '$state', 'menu',
    'notification', '$modal', 'NgTableParams', '$stateParams'
];

export default taskgridcomponent;
