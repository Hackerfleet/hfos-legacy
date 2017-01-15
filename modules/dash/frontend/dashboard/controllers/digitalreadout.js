'use strict';

var humanizeDuration = require('humanize-duration');

class DigitalReadout {
    constructor($scope, socket, interval) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;

        this.valuetype = this.scope.$parent.valuetype;
        this.value = 0;
        this.age = 0;

        console.log('[DASH-DR] Digitalreadout loaded, observing:', this.valuetype);

        var self = this;

        this.updateAge = function() {
            var seconds = new Date() / 1000;
            if (self.age === 0) {
                self.agehumanized = 'Unknown';
            } else {
                self.agehumanized = humanizeDuration(self.age - seconds, {round:true});
            }
        };

        this.handleNavdata = function (msg) {
            //console.log('[DASH-DR] NAVDATA: ', msg, self.valuetype);
            if (msg.data.type === self.valuetype) {
                var data = msg.data;

                //console.log('[DASH-DR] Updating Digitalreadout: ', data, data.value, data.type);
                self.value = data.value;
                self.age = data.timestamp;
                self.updateAge();
                self.scope.$apply();
            }
        };

        this.interval(this.updateAge, 1000);

        self.socket.listen('navdata', self.handleNavdata);
        
        self.scope.$on('$destroy', function() {
            console.log('[DASH-DR] UNLISTENING');
            self.socket.unlisten('navdata', self.handleNavdata);
        });
    }
}

DigitalReadout.$inject = ['$scope', 'socket', '$interval'];

export default DigitalReadout;
