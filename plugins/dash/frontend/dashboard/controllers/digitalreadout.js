'use strict';

console.log("Hello, digitalreadout has been loaded.");

class DigitalReadout {
    constructor() {
        this.valuetype = this.$parent.valuetype;
        this.value = 0;

        console.log('Hello. I am here!');

        var self = this;
        console.log(self);

        this.$on('hfos.NavdataUpdate', function (event, frame) {
            self.value = frame[self.valuetype];
            //this.$apply();
        });
    }
}

export default DigitalReadout;
