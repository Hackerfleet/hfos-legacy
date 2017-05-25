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

/**
 * Created by riot on 14.05.16.
 */

const widgettypes = ['compare_int']; //, 'find'];

const widgettemplates = {};

for (var item of widgettypes) {
    widgettemplates[item] = require('../templates/' + item + '.tpl.html');
}

console.log('[NGAT] Dynamic widgets:', widgettemplates);

var automattoolcontroller = function ($compile, $http, $parse) {
    console.log('[NGDC] Init.');
    return {
        restrict: 'A',
        transclude: true,
        terminal: true,
        priority: 100000,
        scope: {
            ctrl: "=ngAutomatTool",
            function: "=",
            argument: "="
        },
        link: function (scope, elem, attrs) {
            function update_controller() {
                let ctrl = scope.ctrl;
                elem.removeAttr('ng-automat-tool');
                elem.empty();
                elem.append(widgettemplates[ctrl]);
                $compile(elem)(scope);
                elem.attr('ng-automat-tool', ctrl);
            }
            
            scope.$watch('ctrl', function (v) {
                console.log('value changed, new value is: ' + v);
                update_controller();
            });
            
        }
    };
};

automattoolcontroller.$inject = ['$compile', '$http', '$parse'];

export default automattoolcontroller;
