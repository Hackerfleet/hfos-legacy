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
    constructor($scope, $rootScope, $timeout, user, ObjectProxy, state, menu, notification, modal) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;
        this.menu = menu;
        this.notification = notification;
        this.modal = modal;

        this.columns = {};
        this.columnsize = 4;

        this.tasklist = {};

        this.taskgridconfig = {};
        this.taskgridconfiguuid = "";
        this.taskgroups = {};
        this.tasksByGroup = {};

        this.tags = {};
        this.projects = {};

        this.filter_tag = "";
        this.filter_project = "";

        this.show_filters = false;
        this.show_filters_tag = false;
        this.show_filters_project = false;

        this.selected = [];
        this.selected_groups = [];

        this.target_group = null;

        this.search_string = '';

        this.changetimeout = null;
        this.lockState = false;

        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 100,
            rowHeight: 100,
            colWidth: 100,
            mobileBreakPoint: 200,
            draggable: {
                enabled: false
            },
            resizable: {
                enabled: false
            }
        };

        let self = this;

        this.switchtaskgridconfig = function (uuid) {
            self.taskgridconfiguuid = uuid;
            self.op.getObject('taskgridconfig', uuid);
        };

        this.storeTaskGridConfig = function () {
            console.log('[TASKGRID] Pushing taskgridconfig');

            for (let card of self.taskgridconfig.cards) {
                delete card['$$hashKey'];
            }
            self.op.putObject('taskgridconfig', self.taskgridconfig);

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

        this.rootscope.$on('Clientconfig.Update', function () {
            self.gettaskgridconfig();
        });

        if (typeof user.clientconfig.taskgridconfiguuid !== 'undefined') {
            this.gettaskgridconfig();
        }

        this.scope.$on('OP.Get', function (event, uuid, object, schema) {
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

        this.scope.$on('OP.ListUpdate', function (event, schema) {
            if (schema === 'taskgridconfig') {
                self.taskgrids = self.op.lists.taskgridconfig;
            }
        });

        this.rootscope.$on('User.Login', function () {
            console.log('[TASKGRID] Login successful - fetching taskgridconfig data');
            self.gettaskgridconfig();
        });

        if (this.user.signedin === true) {
            console.log('[TASKGRID] Logged in - fetching taskgridconfig data');
            this.gettaskgridconfig();
        }
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
        console.log('[TASKGRID] Getting list of taskgridconfigs');
        this.op.getList('taskgridconfig');
        let self = this;
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

        console.log('[TASKGRID] Getting configured taskgridconfig');
        /*
        // TODO: Pull module default configurations from a service
        let uuid = self.user.clientconfig.modules.taskgriduuid;

        console.log('[TASKGRID] Clientconfig Taskgrid UUID: ', self.taskgriduuid);

        if (uuid === '' || typeof uuid === 'undefined') {
            console.log('[TASKGRID] Picking user profile taskgrid', self.user.profile);
            uuid = self.user.profile.modules.taskgriduuid;
        }
        if (uuid === '' || typeof uuid === 'undefined') {
            console.log('[TASKGRID] Picking system profile taskgrid', self.systemconfig.config);
            uuid = self.systemconfig.config.modules.taskgriduuid;
        }
        console.log('[TASKGRID] Final Taskgrid UUID: ', uuid);

        this.taskgridconfiguuid = uuid;
        */

        this.taskgridconfiguuid = this.user.getModuleDefault('taskgriduuid');

        console.log('[TASKGRID] Config: ', this.taskgridconfiguuid);
        this.op.getObject('taskgridconfig', this.taskgridconfiguuid);
    }

    new_task(group_uuid) {
        console.log('[TASKGRID] Adding new task to group:', group_uuid);
        this.state.go('app.editor', {schema: 'task', action: 'create', initial: {taskgroup: group_uuid}})
    }

    select_all() {
        this.selected = [];
        for (let uuid of Object.keys(this.tasklist)) {
            let task = this.tasklist[uuid];

            let name = task.name.toLowerCase(),
                search = this.search_string.toLowerCase(),
                description = "";
            if (typeof task.description !== 'undefined') description = task.description.toLowerCase();

            console.log('[TASKGRID] Filters:', name, description, search);

            if ((name.indexOf(search) > -1 || description.indexOf(search) > -1) &&
                (this.show_filters_project ? this.filter_project === task.project : true) &&
                ((this.show_filters_tag ? task.tags.indexOf(this.filter_tag) > -1 : true) ||
                    (this.show_filters_tag && this.filter_tag === '' && task.tags.length === 0))
            ) {
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
        if (typeof this.tag === 'undefined' || this.tag === null || this.tag === '') {
            this.notification.add('warning', 'Select a tag first', 'You have to select a tag to add.', 3);
            return
        }

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            console.log(task);

            if (task.tags.indexOf(this.tag) < 0) {
                console.log('[TASKGRID] Adding tag.');
                task.tags.push(this.tag);

                this.op.changeObject('task', uuid, {field: 'tags', 'value': task.tags});
            }
        }
    }

    remove_tags() {
        if (typeof this.tag === 'undefined' || this.tag === null || this.tag === '') {
            this.notification.add('warning', 'Select a tag first', 'You have to select a tag to be removed.', 3);
            return
        }

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];

            if (task.tags.indexOf(this.tag) >= 0) {
                task.tags.splice(task.tags.indexOf(this.tag), 1);
                this.op.changeObject('task', uuid, {field: 'tags', 'value': task.tags});
            }
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
            this.op.deleteObject('task', uuid).then(function(response) {
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
        if (typeof this.target_group === 'undefined' || this.target_group === null || this.target_group === '') {
            this.notification.add('warning', 'Select a target group', 'You have to select a target group to mass move tasks.', 3);
            return
        }

        console.log('[TASKGRID] Moving Tasks');

        for (let uuid of this.selected) {
            let task = this.tasklist[uuid];
            let old_group = this.tasksByGroup[task.taskgroup];

            old_group.splice(old_group.indexOf(task), 1);

            this.tasksByGroup[this.target_group].push(task);

            task.taskgroup = this.target_group;

            this.op.changeObject('task', uuid, {'field': 'taskgroup', 'value': this.target_group});
        }
    }

    opentab(tabname) {
        console.log('[TASKGRID] Switching tab to ', tabname);
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
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

taskgridcomponent.$inject = ['$scope', '$rootScope', '$timeout', 'user', 'objectproxy', '$state', 'menu', 'notification', '$modal'];

export default taskgridcomponent;
