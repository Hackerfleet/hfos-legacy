'use strict';

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:SharingCtrl
 * @description
 * # SharingCtrl
 * Controller of the hfosFrontendApp
 */
class SharingCtrl {
    constructor($scope, $compile, ObjectProxy, moment, alert, socket) {
        this.scope = $scope;
        this.compile = $compile;
        this.moment = moment;
        this.op = ObjectProxy;
        this.alert = alert;
        this.socket = socket;
        
        let now = new Date();
        
        this.shareables = [];
    
        let self = this;
        this.op.searchItems('shareable').then(function(result) {
            console.log('[SHAREABLES] Got the list of shareables:', result, self.reservationlookup);
            self.reservationlookup = result.data;
            self.reservationtarget = self.reservationlookup[0]['uuid'];
        });
    
        this.reservationtarget = '';
    
        this.reserve_from = '';
        this.reserve_to = '';
              
        this.calendarView = 'week';
        this.calendarDate = new Date();
        this.calendarTitle = 'Shareables for %NAME';
        
        let editaction = {
            label: '<i class=\'glyphicon glyphicon-pencil\'></i>',
            onClick: function (args) {
                alert.add('success', 'Edited', args.calendarEvent, 5);
            }
        };
        
        let delaction = {
            label: '<i class=\'glyphicon glyphicon-remove\'></i>',
            onClick: function (args) {
                alert.add('success', 'Deleted', args.calendarEvent, 5);
            }
        };
        
        let actions = [editaction, delaction];
        
        const eventcolor = {
            primary: 'lightgray',
            secondary: 'darkgray'
        };
        
        this.events = [];
        
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
            alert.add('success', 'Clicked', String(event), 10);
        };
        
        
        this.eventTimesChanged = function (event) {
            alert.show('Dropped or resized', event);
        };
        
        this.toggle = function ($event, field, event) {
            $event.preventDefault();
            $event.stopPropagation();
            event[field] = !event[field];
        };
        
        this.getReservations = function() {
            this.op.getList('shareable', {'reservations': {'$elemMatch': {'endtime': {'$gt': now}}}}, ['*']);
        };
        
        this.getReservations();
        
        this.updateTimetable = function () {
            self.events = [];
            for (let shareable of self.shareables) {
                console.log('Analyzing thing: ', shareable);
                
                for (let res of shareable.reservations) {
                    console.log('It has a reservation: ', res);
                    let calItem = {
                        title: shareable.name + ': ' + res.title,
                        url: '#!/editor/shareable/' + shareable.uuid,
                        startsAt: new Date(Date.parse(res.starttime)),
                        endsAt: new Date(Date.parse(res.endtime)),
                        color: '#ff0000',
                        draggable: true,
                        resizable: true
                    };
                    
                    console.log(res.starttime, new Date(Date.parse(res.starttime)), new Date(res.starttime));
                    
                    self.events.push(calItem);
                }
            }
            
            console.log('Calendar: ', self.events);
        };
        
        this.scope.$on('OP.ListUpdate', function (ev, schema) {
            if (schema === 'shareable') {
                self.shareables = self.op.list('shareable');
                self.updateTimetable();
            }
        });
        this.socket.listen("hfos.shareables.manager", function(msg) {
             if (msg.action == 'reserve') {
                 if (msg.data == true) {
                     self.alert.add('success', 'Reserved', 'Your reservation has been accepted.', 10);
                     self.getReservations();
                 } else {
                     self.alert.add('danger', 'Blocked', 'The shareable is already reserved during that time.', 10);
                 }
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
    
    reserve() {
        let reservation = {
            component: 'hfos.shareables.manager',
            action: 'reserve',
            data: {
                uuid: this.reservationtarget,
                from: this.reserve_from,
                to: this.reserve_to
            }
        };
        
        console.log('[SHAREABLE] Requesting reservation:', reservation);
        this.socket.send(reservation);
    }
}

SharingCtrl.$inject = ['$scope', '$compile', 'objectproxy', 'moment', 'alert', 'socket'];

export default SharingCtrl;