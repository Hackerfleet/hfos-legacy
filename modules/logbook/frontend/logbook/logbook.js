'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:LogbookCtrl
 * @description
 * # LogbookCtrl
 * Controller of the hfosFrontendApp
 */
class LogbookCtrl {
    constructor($scope, $compile, ObjectProxy, moment, notification) {
        this.scope = $scope;
        this.compile = $compile;
        this.moment = moment;
        this.op = ObjectProxy;
        
        console.log('Hello, i am a logbook view controller!');
        
        let now = new Date();
        
        this.op.getList('logbookentry', {}, ['*']);
        
        this.shareables = [];
        this.reservationlookup = {};
        
        let self = this;
        
        this.foobar = 1;
        
        this.calendarView = 'week';
        this.calendarDate = new Date();
        this.calendarTitle = 'Logbook entries for %NAME';
        
        let editaction = {
            label: '<i class=\'glyphicon glyphicon-pencil\'></i>',
            onClick: function (args) {
                notification.add('success', 'Edited', args.calendarEvent, 5);
            }
        };
        
        let delaction = {
            label: '<i class=\'glyphicon glyphicon-remove\'></i>',
            onClick: function (args) {
                notification.add('success', 'Deleted', args.calendarEvent, 5);
            }
        };
        
        let actions = [editaction, delaction];
        
        const eventcolor = {
            primary: 'red',
            secondary: 'white'
        };
        
        this.events = [
            {
                title: 'An event',
                color: eventcolor,
                startsAt: this.moment().startOf('week').subtract(2, 'days').add(8, 'hours').toDate(),
                endsAt: this.moment().startOf('week').add(1, 'week').add(9, 'hours').toDate(),
                draggable: true,
                resizable: true,
                actions: actions
            }, {
                title: '<i class="glyphicon glyphicon-asterisk"></i> <span class="text-primary">Another event</span>, with a <i>html</i> title',
                color: eventcolor,
                startsAt: this.moment().subtract(1, 'day').toDate(),
                endsAt: this.moment().add(5, 'days').toDate(),
                draggable: true,
                resizable: true,
                actions: actions
            }, {
                title: 'This is a really long event title that occurs on every year',
                color: eventcolor,
                startsAt: this.moment().startOf('day').add(7, 'hours').toDate(),
                endsAt: this.moment().startOf('day').add(19, 'hours').toDate(),
                recursOn: 'year',
                draggable: true,
                resizable: true,
                actions: actions
            }
        ];
        
        this.isCellOpen = true;
        
        this.addEvent = function () {
            this.events.push({
                title: 'New event',
                startsAt: this.moment().startOf('day').toDate(),
                endsAt: this.moment().endOf('day').toDate(),
                color: '#ff0000',
                draggable: true,
                resizable: true
            });
        };
        
        this.eventClicked = function (event) {
            notification.add('success', 'Clicked', String(event), 10);
        };
        
        
        this.toggle = function ($event, field, event) {
            $event.preventDefault();
            $event.stopPropagation();
            event[field] = !event[field];
        };
        
        this.updateTimetable = function () {
            for (let entry of self.entries) {
                console.log('Analyzing thing: ', entry);
                let calItem = {
                    title: entry.name + ': ' + entry.title,
                    url: '#!/editor/logbookentry/' + entry.uuid,
                    startsAt: new Date(Date.parse(entry.starttime)),
                    endsAt: new Date(Date.parse(entry.starttime + 1)),
                    color: '#ff0000',
                    draggable: false,
                    resizable: false
                };
    
                self.events.push(calItem);
            }
            
            console.log('Calendar: ', self.events);
        };
        
        this.scope.$on('OP.ListUpdate', function (ev, schema) {
            if (schema == 'logbookentry') {
                self.entries = self.op.list('logbookentry');
                self.updateTimetable();
            }
        });
        
        this.eventRender = function (event, element, view) {
            console.log("HALLO: ", event, element, view);
            element.attr({
                'tooltip': event.title,
                'tooltip-append-to-body': true
            });
            self.compile(element)(self);
        };
    }
}

LogbookCtrl.$inject = ['$scope', '$compile', 'objectproxy', 'moment', 'notification'];

export default LogbookCtrl;