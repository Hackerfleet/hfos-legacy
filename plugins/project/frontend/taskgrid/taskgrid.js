'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:TaskGridCtrl
 * @description
 * # TaskGridCtrl
 * Controller of the hfosFrontendApp
 */

class taskgridcomponent {
    constructor($scope, user, ObjectProxy, state) {

        ObjectProxy.getList('task', {}, ['name', 'status', 'priority']);

        this.user = user;
        this.state = state;
        this.tasklist = [];
        this.tasks = {};
        this.op = ObjectProxy;

        this.columns = {};

        this.columnsVisible = {
            'Open': 0,
            'Waiting': 1,
            'In progress': 2,
            'Closed': 3,
            'Resolved': -1,
            'Duplicate': -1,
            'Invalid': -1,
            'Cannot reproduce': -1
        };
    
        var self = this;
        
        this.updateVisibleColumns = function() {
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
            console.log('Tasks', self.columns);
        };

        this.populateHeaders = function() {
            $.each(self.columnsVisible, function (key, value) {
                if (value !== -1) {
                    self.columns[key] = [];
                }
            });
            console.log(self.items);
        };

        $scope.$on('OP.ListUpdate', function (event, schema) {
            self.tasklist = self.op.lists[schema];

            console.log(self.tasklist);
            self.updateVisibleColumns();
        });

        this.updateVisibleColumns();
    }

    opentab(tabname) {
        console.log('[TASKGRID] Switching tab to ', tabname);
        $('.nav-pills .active, .tab-content .active').removeClass('active');
        $('#' + tabname).addClass('active');
    }

    addTask() {
        console.log('[TASKGRID] Switching to add task view');
        this.state.go('app.editor', {schema: 'task', action: 'edit', 'uuid': 'create'});
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

taskgridcomponent.$inject = ['$scope', 'user', 'objectproxy', '$state'];

export default taskgridcomponent;
