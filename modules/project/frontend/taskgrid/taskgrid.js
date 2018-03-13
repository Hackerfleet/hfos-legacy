'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TaskGridCtrl
 * @description
 * # TaskGridCtrl
 * Controller of the hfosFrontendApp
 */

class taskgridcomponent {
    constructor($scope, $rootScope, $timeout, user, ObjectProxy, state, menu) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;
        this.menu = menu;

        this.columns = {};
        this.columnsize = 4;

        this.tasklist = {};

        this.taskgridconfig = {};
        this.taskgridconfiguuid = "";
        this.taskgroups = {};
        this.tasksByGroup = {};

        this.tags = {};
        this.projects = {};

        this.search_string = '';

        this.changetimeout = null;
        this.lockState = false;

        this.gridsterOptions = {
            // any options that you can set for angular-gridster (see:  http://manifestwebdesign.github.io/angular-gridster/)
            columns: screen.width / 100,
            rowHeight: 400,
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
                let taskgridconfiglist = self.op.lists.taskgridconfig;
                let taskgridconfigmenu = [];
                for (let taskgridconfig of taskgridconfiglist) {
                    taskgridconfigmenu.push({
                        type: 'func',
                        name: taskgridconfig.uuid,
                        text: taskgridconfig.name,
                        callback: self.switchtaskgridconfig,
                        args: taskgridconfig.uuid
                    });
                }
                self.menu.removeMenu('Taskgrids');
                self.menu.addMenu('Taskgrids', taskgridconfigmenu);
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
        let uuid = this.user.clientconfig.taskgriduuid;

        if (typeof uuid === 'undefined') {
            uuid = this.user.profile.settings.taskgriduuid;
        }
        this.taskgridconfiguuid = uuid;

        console.log('[TASKGRID] Config: ', this.taskgridconfiguuid);
        this.op.getObject('taskgridconfig', this.taskgridconfiguuid);
    }

    new_task(group_uuid) {
        console.log('[TASKGRID] Adding new task to group:', group_uuid);
        this.state.go('app.editor', {schema: 'task', action: 'create', initial: {taskgroup: group_uuid}})
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

taskgridcomponent.$inject = ['$scope', '$rootScope', '$timeout', 'user', 'objectproxy', '$state', 'menu'];

export default taskgridcomponent;
