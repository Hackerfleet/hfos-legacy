/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2018 riot <riot@c-base.org> and others.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

'use strict';

let humanizeDuration = require('humanize-duration');

class DigitalReadout {
    constructor($scope, socket, interval, moment) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;
        this.moment = moment;

        console.log('[CLOCK] Valuetype:', this.scope.$parent.valuetype, this.scope);
        if (typeof this.valuetype !== 'undefined') {
            this.valuetype = JSON.parse(this.scope.$parent.valuetype);
        } else {
            this.valuetype = {source: null, timezone: null, format: null};
        }

        this.source = this.valuetype.source;
        this.timezone = this.valuetype.timezone;
        this.format = this.valuetype.format;

        this.value = 0;
        this.age = 0;

        if (this.source === null) this.source = "Client";
        if (this.timezone === null) this.timezone = "UTC";
        if (this.format === null) this.format = 'hh:mm:ss';

        this.formats = [
            'hh:mm:ss',
            'h:mm:ss a'
        ];

        console.log('[DASH-CLOCK] Clock loaded, observing:', this.valuetype, this.source, this.timezone, this.format);

        let self = this;
        
        self.scope.$on('resize', function (event, new_size) {
            console.log('Resizing to:', new_size);
            self.width = new_size[0];
            self.height = new_size[1];
        });

        this.updateClock = function() {
            self.value = self.moment(new Date());
            self.value = self.value.tz(self.timezone);
            self.value = self.value.format(self.format);
            console.debug(self.value);
        };

        this.update_valuetype = function() {
            if (this.timezone === null || this.source === null || this.format === null) return;

            this.valuetype = JSON.stringify({
                timezone: this.timezone,
                source: this.source,
                format: this.format
            });
            //this.scope.$parent.valuetype = this.valuetype;
            this.scope.$emit('Dash.Store', {
                y: self.scope.$parent.gridsterItem.col,
                x: self.scope.$parent.gridsterItem.row,
                valuetype: self.valuetype
            });
            console.log(this.scope, this.scope.$parent);
        };

        this.updater = this.interval(this.updateClock, 250);

        this.scope.$on('$destroy', function() {
            console.log('DESTROYING...');
            self.interval.cancel(self.updater);
        })
    }
}

DigitalReadout.$inject = ['$scope', 'socket', '$interval', 'moment'];

export default DigitalReadout;
