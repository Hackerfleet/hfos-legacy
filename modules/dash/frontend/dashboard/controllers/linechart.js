/*
 * #!/usr/bin/env python
 * # -*- coding: UTF-8 -*-
 *
 * __license__ = """
 * Hackerfleet Operating System
 * ============================
 * Copyright (C) 2011- 2017 riot <riot@c-base.org> and others.
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

class LineChart {
    constructor($scope, socket, interval, element) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;
        this.element = element;
        
        this.valuetype = this.scope.$parent.valuetype;
        
        this.values = [];
        this.ages = [];
        this.ages_humanzied = [];
        
        this.history_length = 10;
        
        console.log('[DASH-LC] LineChart loaded, observing:', this.valuetype);
        
        this.options = {
            data: [],
            dimensions: {
                timestamp: {
                    axis: 'x'
                }
            },
            chart: {
                size: {
                    width: 300,
                    height: 200
                }
            }
        };
        
        this.instance = null;
        
        let self = this;
        
        self.scope.$on('resize', function (event, new_size) {
            console.log('Resizing to:', new_size);
            self.options.chart.size = {
                width: new_size[0] - 20,
                height: new_size[1] - 20
            }
        });
        
        this.updateAges = function () {
            let seconds = new Date() / 1000;
            self.ages_humanized = [];
            for (let age of self.ages) {
                if (age === 0) {
                    self.ages_humanized.push('Unknown');
                } else {
                    self.ages_humanized = humanizeDuration(age - seconds, {round: true});
                }
            }
        };
        
        this.handleNavdata = function (msg) {
            //console.log('[DASH-LC] NAVDATA: ', msg, self.valuetype);
            if (typeof msg.data.timestamp !== 'undefined') {
                let data = msg.data;
                console.log('DATA:', data);
                
                if (typeof self.options.dimensions[data.type] === 'undefined') {
                    self.options.dimensions[data.type] = {
                        type: 'line'
                    };
                    
                }
                
                //console.log('[DASH-LC] Updating LineChart: ', data, data.value, data.type);
                let content = {};
                content[data.type] = data.value;
                
                let date = new Date(data.timestamp * 1000);
                let hours = date.getHours();
                let minutes = "0" + date.getMinutes();
                let seconds = "0" + date.getSeconds();
                
                content.timestamp = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
                
                self.options.data.push(content);
                self.ages.push(data.timestamp);
                if (self.options.data.length > self.history_length) {
                    self.options.data.shift()
                }
                self.updateAges();
                self.scope.$apply();
            }
        };
        
        this.interval(this.updateAges, 1000);
        
        self.socket.listen('hfos.navdata.sensors', self.handleNavdata);
        
        self.scope.$on('$destroy', function () {
            console.log('[DASH-LC] UNLISTENING');
            self.socket.unlisten('hfos.navdata.sensors', self.handleNavdata);
        });
        
        
    }
    
    prune_history() {
        let oversize = this.options.data.length - this.history_length;
        if (oversize > 0) {
            this.options.data.splice(0, oversize);
        }
    }
}

LineChart.$inject = ['$scope', 'socket', '$interval', '$element'];

export default LineChart;
