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
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * """
 */

// Loosely based on: https://github.com/dav-/unit-circle

'use strict';

let d3 = require('d3');

let humanizeDuration = require('humanize-duration');

class SimpleCompass {
    constructor($scope, socket, interval, element) {
        this.scope = $scope;
        this.socket = socket;
        this.interval = interval;
        this.element = element;
        
        this.valuetype = this.scope.$parent.valuetype;
        this.value = 0;
        this.age = 0;
        this.lastAngle = 1.23;
        
        console.log('[DASH-SC] SimpleCompass loaded, observing:', this.valuetype);
        
        // TODO: Resize this upon widget resize:
        this.radius = 100;
        this.width = 350;
        this.height = 350;
        
        this.updateAge = function () {
            let seconds = new Date() / 1000;
            if (self.age === 0) {
                self.agehumanized = 'Unknown';
            } else {
                self.agehumanized = humanizeDuration(self.age - seconds, {round: true});
            }
        };
        
        this.handleNavdata = function (msg) {
            //console.log('[DASH-SC] NAVDATA: ', msg, self.valuetype);
            if (msg.data.type === self.valuetype) {
                let data = msg.data;
                
                let angle = data.value * (Math.PI / 180);
                console.log('[DASH-SC] Updating SimpleCompass: ', data.value, angle);
                self.value = data.value;
                self.age = data.timestamp;
                self.updateAge();
                self.drawAngleSweep(angle);
                
                self.scope.$apply();
            }
        };
        
        this.interval(this.updateAge, 1000);
        
        let self = this;
        
        self.socket.listen('hfos.navdata.sensors', self.handleNavdata);
        
        self.scope.$on('$destroy', function () {
            self.socket.unlisten('hfos.navdata.sensors', self.handleNavdata);
        });
        
        self.scope.$on('resize', function (event, new_size) {
            console.log('Resizing to:', new_size);
            self.width = new_size[0];
            self.height = new_size[1];
            self.radius = (Math.min(self.width, self.height) - 60) / 2.7;
            self.init_svg();
            self.Compass();
        });
        
        this.init_svg = function () {
            self.rawSvg = element.find('svg');
            d3.selectAll("svg > *").remove();
            
            self.svg = d3.select(self.rawSvg[0])
                .attr("width", self.width)
                .attr("height", self.height)
                .append("g")
                .attr("transform", "translate(" + self.width / 2 + "," + self.height / 2 + ") scale(1, -1)")
                .on("mousedown", function () {
                    console.log(d3.mouse(this))
                });
            
            console.log('[DASH-SC] d3 element: ', self.svg);
        };
        
        this.drawAngleSweep = function (realangle) {
            // TODO: Remove the right element via angular's component element, not via jquery
            $(".angleSweep").remove();
            
            let angle = ((2 * Math.PI - realangle) + Math.PI / 2) % (2 * Math.PI);
            self.lastAngle = angle;
            
            let svg = self.svg,
                width = 2,
                cos = Math.cos(angle),
                sin = Math.sin(angle),
                coords = {
                    x: self.radius * cos,
                    y: self.radius * sin
                };
            
            //Center to circle
            svg.append("line")
                .attr("class", "angleSweep")
                .attr("x1", 0)
                .attr("y1", 0)
                .attr("x2", coords.x)
                .attr("y2", coords.y)
                .style("fill", "none")
                .style("stroke-width", "2px");
            
            
            //Point on circle
            svg.append("circle")
                .attr("class", "angleSweep")
                .attr("cx", coords.x)
                .attr("cy", coords.y)
                .attr("r", 5)
                .style("stroke", "none");
            
        };
        
        this.Compass = function () {
            let svg = self.svg;
            
            //Axes and arrows
            svg.append("line")
                .attr("class", "y compassCross")
                .attr("y1", -(self.radius + 30))
                .attr("y2", (self.radius + 30))
                .style("fill", "none")
                .style("stroke-width", "2px");
            svg.append("line")
                .attr("class", "x compassCross")
                .attr("x1", -(self.radius + 30))
                .attr("x2", (self.radius + 30))
                .style("fill", "none")
                .style("stroke-width", "2px");
            svg.append("polygon")
                .attr("class", "ynArrow compassArrow")
                .attr("points", "0," + (self.radius + 40) + " 5," + (self.radius + 30) + " -5," + (self.radius + 30));
            svg.append("polygon")
                .attr("class", "ypArrow compassArrow")
                .attr("points", "0," + -(self.radius + 40) + " 5," + -(self.radius + 30) + " -5," + -(self.radius + 30));
            svg.append("polygon")
                .attr("class", "xnArrow compassArrow")
                .attr("points", -(self.radius + 40) + ",0 " + -(self.radius + 30) + ",5 " + -(self.radius + 30) + ",-5");
            svg.append("polygon")
                .attr("class", "xpArrow compassArrow")
                .attr("points", (self.radius + 40) + ",0 " + (self.radius + 30) + ",5 " + (self.radius + 30) + ",-5");
            //Center
            svg.append("circle")
                .attr("class", "center compassCenter")
                .attr("r", "5px");
            
            
            //Circle
            svg.append("circle")
                .attr("class", "uc compassArea")
                .attr("r", self.radius)
                .style("stroke-width", "4px");
            
            
            function drawAngleMark(realangle) {
                let angle = ((2 * Math.PI - realangle) + (Math.PI / 2)) % (2 * Math.PI),
                    length = 30,
                    cos = Math.cos(angle),
                    sin = Math.sin(angle),
                    coords = {
                        inner: {
                            x: (self.radius - (length / 2)) * sin,
                            y: (self.radius - (length / 2)) * cos
                        },
                        outer: {
                            x: (self.radius + (length / 2)) * sin,
                            y: (self.radius + (length / 2)) * cos
                        },
                        text: {
                            x: (self.radius + (2 * length)) * sin - length / 2,
                            y: (self.radius + (2 * length)) * cos - length / 4
                        },
                        center: {
                            x: self.radius * sin,
                            y: self.radius * cos
                        }
                    };
                
                //Line mark
                svg.append("line")
                    .attr("class", "angleMark")
                    .attr("x1", coords.inner.x)
                    .attr("y1", coords.inner.y)
                    .attr("x2", coords.outer.x)
                    .attr("y2", coords.outer.y)
                    .style("fill", "none");
                
                if (self.radius > 100) {
                    //Text
                    svg.append("text")
                        .attr("class", "angleText")
                        .attr("x", coords.text.x)
                        .attr("y", coords.text.y)
                        .attr("transform", "matrix(1, 0, 0, -1, " + (coords.text.x - (1) * coords.text.x) + ", " + (coords.text.y - (-1) * coords.text.y) + ")")
                        .text(Math.round(parseFloat((180 / Math.PI) * angle)));
                }
            }
            
            self.drawAngleSweep(self.lastAngle);
            
            function scaleMarks() {
                $('.angleMark').remove();
                
                for (let i = 0; i < 360; i = i + 15) {
                    drawAngleMark(i * (Math.PI / 180));
                }
            }
            
            scaleMarks();
        };
        
        this.init_svg();
        this.Compass();
    }
}

SimpleCompass.$inject = ['$scope', 'socket', '$interval', '$element'];

export default SimpleCompass;
