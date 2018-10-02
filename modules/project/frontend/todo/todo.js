'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TODOCtrl
 * @description
 * # TODOCtrl
 * Controller of the hfosFrontendApp
 */

class TODOcomponent {
    constructor($scope, $rootScope, $timeout, user, ObjectProxy, state) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;

        this.tasklist = [];

        this.tags = {};
        this.projects = [];
        this.projects_lookup = {};
        this.groups = {};

        this.open_groups = [];
        this.closed_group = null;

        this.show_closed = false;
        this.show_priorities = false;
        this.show_max_priority = 10;

        this.filtername = "Assigned to me";
        this.filtered_projects = [];

        this.changetimeout = null;

        let self = this;

        this.get_filtered_tasks = function () {
            console.log('[TODO] Getting list of tasks');
            let groups = this.open_groups.concat(this.closed_group);
            console.log('[TODO] Groups:', groups, this.open_groups, this.closed_group);

            let filter = {
                assignee: this.user.useruuid,
                taskgroup: {'$in': groups}
            };
            console.log(filter);
            this.op.search('task', filter, '*').then(function (msg) {
                console.log('[TODO] Filling task list:', msg.data.list);
                self.tasklist = msg.data.list;
            })
        };

        this.update_lists = function () {
            let self = this;

            this.op.search('taskgroup', '', ['name', 'color']).then(function (msg) {
                for (let group of msg.data.list) {
                    self.groups[group.uuid] = group;
                }
            });

            this.op.search('project').then(function (msg) {
                self.projects = msg.data.list;

                for (let project of msg.data.list) {
                    self.filtered_projects.push(project.uuid);
                    self.projects_lookup[project.uuid] = project;
                }
            });

            this.op.search('tag', '', '*').then(function (msg) {
                for (let tag of msg.data.list) {
                    self.tags[tag.uuid] = tag;
                }
            });
        };

        this.get_settings = function () {
            this.closed_group = this.user.get_module_default('closed_group');
            this.open_groups = this.user.get_module_default('open_groups');
            console.log('[TODO] Settings:', this.closed_group, this.open_groups);
            self.get_filtered_tasks();
        };

        this.rootscope.$on('User.Login', function () {
            self.update_lists();
            self.get_settings()
        });

        if (this.user.signedin === true) {
            self.update_lists();
            self.get_settings()
        }

    }

    increase_priority(task) {
        if (typeof task.priority === 'undefined') task.priority = 9;
        else if (task.priority > 1) task.priority--;

        this.op.changeObject('task', task.uuid, {field: 'priority', value: task.priority});
    }

    decrease_priority(task) {
        if (typeof task.priority === 'undefined') task.priority = 1;
        else if (task.priority < 9) task.priority++;

        this.op.changeObject('task', task.uuid, {field: 'priority', value: task.priority});
    }

    toggle_task(task) {
        console.log('[TODO] Toggling task ', task);
        let previous_group = task.group;
        task.taskgroup = this.closed_group;

        this.op.changeObject('task', task.uuid, {field: 'taskgroup', value: this.closed_group})
            .then(function (msg) {
                console.log('[TODO] Response:', msg);
                if (msg.action === 'fail') {
                    task.taskgroup = previous_group;
                }
            });
    }
}

TODOcomponent.$inject = ['$scope', '$rootScope', '$timeout', 'user', 'objectproxy', '$state'];

export default TODOcomponent;
