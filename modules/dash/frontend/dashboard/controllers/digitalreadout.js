'use strict';

let humanizeDuration = require('humanize-duration');

class DigitalReadout {
    constructor($scope, socket, interval) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;

        this.valuetype = this.scope.$parent.valuetype;
        this.value = 0;
        this.age = 0;

        console.log('[DASH-DR] Digitalreadout loaded, observing:', this.valuetype);

        let self = this;
        
        self.scope.$on('resize', function (event, new_size) {
            console.log('Resizing to:', new_size);
            self.width = new_size[0];
            self.height = new_size[1];
        });
        
        this.updateAge = function() {
            let seconds = new Date() / 1000;
            if (self.age === 0) {
                self.agehumanized = 'Unknown';
            } else {
                self.agehumanized = humanizeDuration(self.age - seconds, {round:true});
            }
        };

        this.handleNavdata = function (msg) {
            //console.log('[DASH-DR] NAVDATA: ', msg, self.valuetype);
            if (msg.data.type === self.valuetype) {
                let data = msg.data;

                //console.log('[DASH-DR] Updating Digitalreadout: ', data, data.value, data.type);
                self.value = data.value;
                self.age = data.timestamp;
                self.updateAge();
                self.scope.$apply();
            }
        };

        this.interval(this.updateAge, 1000);

        self.socket.listen('hfos.navdata.sensors', self.handleNavdata);
        
        self.scope.$on('$destroy', function() {
            console.log('[DASH-DR] UNLISTENING');
            self.socket.unlisten('hfos.navdata.sensors', self.handleNavdata);
        });
    }
}

DigitalReadout.$inject = ['$scope', 'socket', '$interval'];

export default DigitalReadout;
