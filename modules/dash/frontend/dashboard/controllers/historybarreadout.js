/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2016 riot <riot@c-base.org> and others.
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

var humanizeDuration = require('humanize-duration');

class HistoryBarReadout {
    constructor($scope, socket, interval) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;

        this.valuetype = this.scope.$parent.valuetype;
        this.scalevalue = 0;
        this.scaleprop = '0%';
        this.value = 0;
        this.age = 0;
        this.max = 1;

        this.color = '#4384BF';
        
        this.history = [];

        console.log('[DASH-HBR] HistoryBarReadout loaded, observing:', this.valuetype);

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
            //console.log('[DASH-HBR] NAVDATA: ', msg, self.valuetype);
            if (msg.data.type === self.valuetype) {
                var data = msg.data;

                self.value = data.value;
                self.max = Math.max(self.value, self.max);
                self.scalevalue = (data.value / self.max) * 100;
                
                var scaleprop =  String(self.scalevalue) + '%';
                
                if (self.history.length > 10) {
                    self.history.shift();
                }
                self.history.push(scaleprop);
                self.age = data.timestamp;
                self.updateAge();

                //console.log('[DASH-HBR] Updating HistoryBarReadout: ', data, data.value, data.type, self.history);
                self.scope.$apply();
            }
        };

        this.interval(this.updateAge, 1000);
    
        self.socket.listen('navdata', self.handleNavdata);
    
        self.scope.$on('$destroy', function() {
            self.socket.unlisten('navdata', self.handleNavdata);
        });
    }
}

HistoryBarReadout.$inject = ['$scope', 'socket', '$interval'];

export default HistoryBarReadout;
