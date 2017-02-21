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
            this.op.searchItems('task', {'assignee': this.user.useruuid}, '*').then(function(tasks) {
                console.log('[TODO] Filling task list:', tasks.data);
                for (let item of tasks.data) {
                    self.tasklist[item.uuid] = item;
                }
            })
        };
        
        this.update_lists = function() {
            let self = this;
            
            this.op.searchItems('taskgroup').then(function (groups) {
                self.groups = groups.data;
            });
    
            this.op.searchItems('project').then(function (projects) {
                for (let project of projects.data) {
                    self.projects[project.uuid] = project;
                }
            });
    
            this.op.searchItems('tag', '', '*').then(function (tags) {
                for (let tag of tags.data) {
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
