'use strict';

var humanizeDuration = require('humanize-duration');

class SimpleBarReadout {
    constructor($scope, socket, interval) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;

        this.valuetype = this.scope.$parent.valuetype;
        this.scalevalue = 0;
        this.scaleprop = '0%'
        this.value = 0;
        this.age = 0;
        this.max = 1;

        this.color = '#4384BF';

        console.log('[DASH-SBR] SimpleBarReadout loaded, observing:', this.valuetype);

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
            console.log('[DASH-SBR] NAVDATA: ', msg, self.valuetype);
            if (msg.data.type === self.valuetype) {
                var data = msg.data;

                self.value = data.value;
                self.max = Math.max(self.value, self.max);
                self.scalevalue = (data.value / self.max) * 100;
                self.scaleprop =  String(self.scalevalue) + '%';
                self.age = data.timestamp;
                self.updateAge();

                console.log('[DASH-SBR] Updating SimpleBarReadout: ', data, data.value, data.type, self.scalevalue);
                self.scope.$apply();
            }
        };

        this.interval(this.updateAge, 1000);

        self.socket.listen('navdata', this.handleNavdata);
    }
}

SimpleBarReadout.$inject = ['$scope', 'socket', '$interval'];

export default SimpleBarReadout;
