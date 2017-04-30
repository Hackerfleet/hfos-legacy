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

/**
 * @ngdoc function
 * @name hfosFrontendApp.controller:AutomatCtrl
 * @description
 * # AutomatCtrl
 * Controller of the hfosFrontendApp
 */
class AutomatCtrl {
    constructor($scope, $compile, ObjectProxy, moment, alert) {
        
        this.demorule = {
            eventname: 'hfos.navdata.events.sensordata',
            logic: {
                argument: 'DBT_depth_meters',
                tool: 'compare_int',
                mode: 'lower_equal',
                value: 20
            },
            output: {
                eventname: 'hfos.alert.broadcast',
                data: {
                    type: 'danger',
                    title: 'Depth alert!',
                    msg: 'Depth reached a critical minimum of 20m below keel!',
                    duration: 10
                }
            },
            enabled: true
        };
        
        this.rules = [this.demorule];
    }
}

AutomatCtrl.$inject = ['$scope', '$compile', 'objectproxy', 'moment', 'alert'];

export default AutomatCtrl;
