'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TODOCtrl
 * @description
 * # TODOCtrl
 * Controller of the hfosFrontendApp
 */

class TODOcomponent {
    constructor($scope, $rootScope, $timeout, user, ObjectProxy, state, menu) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.timeout = $timeout;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;

        this.tasklist = {};

        this.tags = {};
        this.projects = {};
        this.groups = [];

        this.filtername = "Assigned to me";
        this.closed_status = null;

        this.changetimeout = null;

        let self = this;

        this.get_filtered_tasks = function() {
            console.log('[TODO] Getting list of tasks');
            this.op.search('task', {'assignee': this.user.useruuid}, '*').then(function(msg) {
                let tasks = msg.data.list;
                console.log('[TODO] Filling task list:', tasks);
                for (let item of tasks) {
                    self.tasklist[item.uuid] = item;
                }
            })
        };

        this.update_lists = function() {
            let self = this;

            this.op.search('taskgroup').then(function (msg) {
                self.groups = msg.data.list;
            });

            this.op.search('project').then(function (msg) {
                for (let project of msg.data.list) {
                    self.projects[project.uuid] = project;
                }
            });

            this.op.search('tag', '', '*').then(function (msg) {
                for (let tag of msg.data.list) {
                    self.tags[tag.uuid] = tag;
                }
            });
        };

        this.rootscope.$on('User.Login', function () {
            self.get_filtered_tasks();
            self.update_lists();
        });

        if (this.user.signedin === true) {
            this.get_filtered_tasks();
            self.update_lists();
        }

    }

    toggle_task(uuid) {
        console.log('[TODO] Toggling task ', uuid);
        this.tasklist[uuid].status = this.closed_status;
    }

    opentab(tabname) {
        console.log('[TODO] Switching tab to ', tabname);
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
    }
}

TODOcomponent.$inject = ['$scope', '$rootScope', '$timeout', 'user', 'objectproxy', '$state', 'menu'];

export default TODOcomponent;
