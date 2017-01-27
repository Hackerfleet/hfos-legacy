'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TaskGridCtrl
 * @description
 * # TaskGridCtrl
 * Controller of the hfosFrontendApp
 */

class taskgridcomponent {
    constructor($scope, $rootScope, user, ObjectProxy, state, menu) {
        this.scope = $scope;
        this.rootscope = $rootScope;
        this.user = user;
        this.state = state;
        this.op = ObjectProxy;
        this.menu = menu;

        this.columns = {};
        this.columnsize = 4;
    
        this.tasklist = [];
        
        this.taskgridconfig = {};
        this.taskgroups = {};
        this.tasks = {};
        
        var self = this;
        
        this.updateVisibleColumns = function() {
            /*
            self.items = [];
            self.populateHeaders();
            
            for (var task of self.tasklist) {
                console.log(self.columns, task.status);
                if (self.columnsVisible[task.status] !== -1) {
                    var newitem = {
                        'name': task.name,
                        'uuid': task.uuid,
                        'drag': true,
                        'priority': task.priority,
                        'status': task.status,
                        'url': 'obj/task/' + task.uuid + '/edit',
                        'row': task.priority
                    };
                    self.columns[task.status].push(newitem);
                }
            }
            

            self.columnsize = 12 / Object.keys(self.columns).length;
            console.log('COLUMNS:', self.columnsize);
            console.log('Tasks', self.columns);
            */
        };
        
        this.switchtaskgridconfig = function (uuid) {
            self.taskgridconfiguuid = uuid;
            self.op.getObject('taskgridconfig', uuid);
        };
        
        this.requesttaskgridconfigs = function () {
            console.log('[TASKGRID] Getting list of taskgridconfigs');
            self.op.getList('taskgridconfig');
        };
               
        this.populateHeaders = function() {
            /*
            $.each(self.columnsVisible, function (key, value) {
                if (value !== -1) {
                    self.columns[key] = [];
                }
            });
            console.log(self.items);
            */
        };
    
        this.rootscope.$on('Clientconfig.Update', function () {
            self.gettaskgridconfig();
        });
    
        if (typeof user.clientconfig.taskgridconfiguuid !== 'undefined') {
            this.gettaskgridconfig();
        }
    
        this.scope.$on('OP.ListUpdate', function (event, schema) {
            if (schema === 'taskgridconfig') {
                var taskgridconfiglist = self.op.lists.taskgridconfig;
                var taskgridconfigmenu = [];
                for (var taskgridconfig of taskgridconfiglist) {
                    taskgridconfigmenu.push({
                        type: 'func',
                        name: taskgridconfig.uuid,
                        text: taskgridconfig.name,
                        callback: self.switchtaskgridconfig,
                        args: taskgridconfig.uuid
                    });
                }
                self.menu.addMenu('taskgridconfigs', taskgridconfigmenu);
            }
        });
        
        this.rootscope.$on('User.Login', function () {
            console.log('[TASKGRID] Login successful - fetching taskgridconfig data');
            self.requesttaskgridconfigs();
        });
    
        if (this.user.signedin === true) {
            console.log('[TASKGRID] Logged in - fetching taskgridconfig data');
            this.requesttaskgridconfigs();
        }
        $scope.$on('OP.ListUpdate', function (event, schema) {
            self.tasklist = self.op.lists[schema];

            console.log(self.tasklist);
            self.updateVisibleColumns();
        });

        this.updateVisibleColumns();
    }
    
    
    gettaskgridconfig() {
        console.log('[TASKGRID] Getting newly configured taskgridconfig');
        this.taskgridconfiguuid = this.user.clientconfig.taskgridconfiguuid;
        this.op.getObject('taskgridconfig', this.taskgridconfiguuid);
    }
    
    opentab(tabname) {
        console.log('[TASKGRID] Switching tab to ', tabname);
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
    }

    onDropComplete(task, ev, status) {
        console.log('DropComplete: ', task, ev, status);
        var tasklist = this.columns[task.status];
        console.log(this.columns[task.status]);

        this.columns[task.status].splice(tasklist.indexOf(task), 1);
        task.status = status;


        this.columns[status].push(task);
        console.log(this.columns);

        this.op.changeObject('task', task.uuid, {'field': 'status', 'value': task.status});
    }
}

taskgridcomponent.$inject = ['$scope', '$rootScope', 'user', 'objectproxy', '$state', 'menu'];

export default taskgridcomponent;
